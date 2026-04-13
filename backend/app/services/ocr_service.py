from __future__ import annotations

import base64
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings


class OCRServiceError(RuntimeError):
    pass


@dataclass
class OCRReadiness:
    ok: bool
    status: str
    message: str
    detail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "message": self.message,
            "detail": self.detail,
        }


_TOKEN_CACHE: dict[str, Any] = {"access_token": None, "expires_at": 0.0}


def _settings():
    return get_settings()


def _check_config() -> None:
    settings = _settings()
    if not settings.BAIDU_OCR_API_KEY or not settings.BAIDU_OCR_SECRET_KEY:
        raise OCRServiceError("BAIDU_OCR_API_KEY / BAIDU_OCR_SECRET_KEY 未配置")


def _get_access_token(force_refresh: bool = False) -> str:
    _check_config()
    now = time.time()
    if not force_refresh and _TOKEN_CACHE["access_token"] and _TOKEN_CACHE["expires_at"] > now + 60:
        return str(_TOKEN_CACHE["access_token"])

    settings = _settings()
    params = {
        "grant_type": "client_credentials",
        "client_id": settings.BAIDU_OCR_API_KEY,
        "client_secret": settings.BAIDU_OCR_SECRET_KEY,
    }
    try:
        with httpx.Client(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            response = client.post(settings.BAIDU_OCR_TOKEN_URL, params=params)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise OCRServiceError(f"OCR Token 接口返回错误：HTTP {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise OCRServiceError(f"OCR Token 请求失败：{exc}") from exc

    data = response.json()
    token = data.get("access_token")
    if not token:
        raise OCRServiceError(f"OCR Token 响应异常：{data}")
    expires_in = int(data.get("expires_in") or 0)
    _TOKEN_CACHE["access_token"] = token
    _TOKEN_CACHE["expires_at"] = now + max(expires_in - 60, 60)
    return str(token)


def check_ocr_readiness(*, live: bool = False) -> OCRReadiness:
    settings = _settings()
    if not settings.BAIDU_OCR_API_KEY or not settings.BAIDU_OCR_SECRET_KEY:
        return OCRReadiness(False, "missing_config", "未配置 OCR 凭据", {"configured": False})
    if not live:
        return OCRReadiness(True, "configured", "OCR 配置已存在，未执行在线验证", {"configured": True})
    try:
        token = _get_access_token(force_refresh=True)
    except OCRServiceError as exc:
        return OCRReadiness(False, "error", str(exc), {"configured": True})
    return OCRReadiness(True, "ready", "OCR 在线校验成功", {"configured": True, "token_prefix": token[:8]})


def extract_text_from_image_bytes(data: bytes) -> dict[str, Any]:
    token = _get_access_token()
    settings = _settings()
    payload = {
        "image": base64.b64encode(data).decode("utf-8"),
        "paragraph": "true",
        "language_type": "CHN_ENG",
    }
    try:
        with httpx.Client(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            response = client.post(
                settings.BAIDU_OCR_GENERAL_URL,
                params={"access_token": token},
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise OCRServiceError(f"OCR 接口返回错误：HTTP {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise OCRServiceError(f"OCR 请求失败：{exc}") from exc

    result = response.json()
    words_result = result.get("words_result") or []
    lines = []
    for item in words_result:
        if isinstance(item, dict) and item.get("words"):
            lines.append(str(item["words"]).strip())
    text = "\n".join(line for line in lines if line)
    if not text.strip():
        raise OCRServiceError(f"OCR 未识别出文本：{result}")
    return {"text": text, "words_count": len(lines), "provider": "baidu_ocr"}
