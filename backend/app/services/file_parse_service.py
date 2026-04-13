from __future__ import annotations

import io

from docx import Document
from pypdf import PdfReader

from app.services.ocr_service import OCRServiceError, extract_text_from_image_bytes


def parse_docx_bytes(data: bytes) -> dict:
    doc = Document(io.BytesIO(data))
    paras = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    text = "\n".join(paras)
    return {"text": text, "paragraphs": len(paras), "parse_mode": "docx_text"}


def parse_pdf_bytes(data: bytes) -> dict:
    reader = PdfReader(io.BytesIO(data))
    parts = []
    ocr_fragments = []
    parse_mode = "pdf_text"
    for page in reader.pages:
        parts.append((page.extract_text() or "").strip())
    text = "\n".join(part for part in parts if part).strip()

    if len(text) < 50:
        parse_mode = "pdf_ocr"
        for page in reader.pages:
            for image in getattr(page, "images", []) or []:
                try:
                    ocr_result = extract_text_from_image_bytes(image.data)
                    if ocr_result.get("text"):
                        ocr_fragments.append(ocr_result["text"])
                except OCRServiceError:
                    continue
        ocr_text = "\n".join(fragment for fragment in ocr_fragments if fragment).strip()
        if ocr_text:
            text = ocr_text
        elif not text:
            raise ValueError("PDF 文本提取为空，且 OCR 未返回可用结果")

    return {"text": text, "pages": len(reader.pages), "parse_mode": parse_mode}


def parse_file_bytes(filename: str, data: bytes) -> dict:
    name = (filename or "").lower()
    if name.endswith(".docx"):
        out = parse_docx_bytes(data)
        out["file_type"] = "docx"
        return out
    if name.endswith(".pdf"):
        out = parse_pdf_bytes(data)
        out["file_type"] = "pdf"
        return out
    raise ValueError("仅支持 .docx / .pdf")

