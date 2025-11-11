from __future__ import annotations
from typing import Optional
from .types import Invoice


def parse_image(path: str, *, lang: str = "deu") -> Invoice:  # pragma: no cover
    """
    Stub for the core parsing routine.

    Expected contract:
      - Accepts a file path to an image or PDF.
      - Performs deskew/threshold, OCR (e.g., Tesseract with `lang`),
        segments header/items/footer, extracts items and totals.
      - Returns a fully-populated `Invoice` object matching `receipt_reader.types.Invoice`.

    Implementation idea (pseudo):
      text, boxes = ocr(path, lang=lang)
      header, body, footer = segment_layout(boxes)
      items = parse_items(body)
      merchant, timestamp = parse_header(header)
      totals = parse_totals(footer)
      return build_invoice(...)

    For now, the function is intentionally unimplemented.
    """
    raise NotImplementedError("parse_image() is not implemented yet")


def parse_text(ocr_text: str) -> Invoice:  # pragma: no cover
    """
    Optional stub if you choose to parse from pre-run OCR text.
    """
    raise NotImplementedError("parse_text() is not implemented yet")
