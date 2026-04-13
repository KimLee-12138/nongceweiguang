from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    ENV: str = 'development'
    # 为了降低首次启动门槛：开发环境默认使用本地 SQLite（仅用于开发/演示）。
    # 生产/联调请在 backend/.env 中显式配置 MySQL DSN。
    MYSQL_DSN: str = 'sqlite:///./dev.db'

    JWT_SECRET_KEY: str = 'dev-insecure-change-me'
    ACCESS_TOKEN_TTL_SECONDS: int = 60 * 30
    REFRESH_TOKEN_TTL_SECONDS: int = 60 * 60 * 24 * 14

    # 开发常见：用 127.0.0.1 和 localhost 打开 Vite 属于不同源，需要都允许。
    CORS_ALLOW_ORIGINS: str = 'http://localhost:5173,http://127.0.0.1:5173'
    TRUST_PROXY_HEADERS: bool = False

    # 启动时按 ORM 幂等补齐常用业务表缺列（create_all 不会 ALTER 已有表）。
    SCHEMA_AUTO_PATCH: bool = True

    DEEPSEEK_API_KEY: str | None = None
    DEEPSEEK_BASE_URL: str = 'https://api.deepseek.com'
    DEEPSEEK_MODEL: str = 'deepseek-chat'
    BAIDU_OCR_API_KEY: str | None = None
    BAIDU_OCR_SECRET_KEY: str | None = None
    BAIDU_OCR_TOKEN_URL: str = 'https://aip.baidubce.com/oauth/2.0/token'
    BAIDU_OCR_GENERAL_URL: str = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'

    HTTP_TIMEOUT_SECONDS: float = 60.0
    CRAWLER_TRUST_ENV_PROXY: bool = False
    HUBEI_CRAWLER_SOURCES_JSON: str = (
        '[{"id":"hubei_agri_policy","name":"湖北省农业农村厅-规范性文件",'
        '"url":"https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/","file_type":"gfxwj"},'
        '{"id":"hubei_agri_other_public","name":"湖北省农业农村厅-其他主动公开文件",'
        '"url":"https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/qtzdgkwj_GK2020/","file_type":"qtzd"},'
        '{"id":"hubei_agri_interpretation","name":"湖北省农业农村厅-政策解读",'
        '"url":"https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/zcjd_GK2020/","file_type":"zcjd"}]'
    )

    def cors_allow_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ALLOW_ORIGINS.split(',') if o.strip()]

    def hubei_crawler_sources(self) -> list[dict[str, Any]]:
        try:
            value = json.loads(self.HUBEI_CRAWLER_SOURCES_JSON)
        except json.JSONDecodeError:
            return []
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict) and item.get('id') and item.get('url')]


@lru_cache
def get_settings() -> Settings:
    return Settings()
