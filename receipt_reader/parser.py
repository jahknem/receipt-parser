from __future__ import annotations

import json
from decimal import Decimal
from typing import Optional
import uuid

from PIL import Image

from .types import Invoice, Item, Merchant, Totals

_processor = None
_model = None


def _get_model():
    """
    Lazily loads and caches the ML model and processor.
    """
    global _processor, _model
    if _processor is None or _model is None:
        try:
            import torch
            from transformers import DonutProcessor, VisionEncoderDecoderModel
        except ImportError as exc:
            raise ImportError(
                "ML dependencies are not installed. Please install them with "
                "'pip install torch transformers sentencepiece'"
            ) from exc

        _processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")
        _model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model.to(device)

    return _processor, _model


def parse_image(path: str, *, lang: str = "deu") -> Invoice:
    """
    Parses a receipt image and returns an Invoice object.
    """
    processor, model = _get_model()

    # Load image
    image = Image.open(path).convert("RGB")

    # Prepare decoder input
    task_prompt = "<s_cord-v2>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids

    # Process image
    pixel_values = processor(image, return_tensors="pt").pixel_values

    # Generate output
    outputs = model.generate(
        pixel_values,
        decoder_input_ids=decoder_input_ids,
        max_length=model.decoder.config.max_position_embeddings,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
        return_dict_in_generate=True,
    )

    # Decode and parse output
    sequence = processor.batch_decode(outputs.sequences)[0]
    sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    sequence = sequence.split("<s_cord-v2>", 1)[-1].strip()

    try:
        data = json.loads(sequence)
    except json.JSONDecodeError:
        return Invoice(
            invoice_id="unknown",
            merchant=Merchant(name="unknown", address="unknown"),
            timestamp="unknown",
            currency="EUR",
            items=[],
            totals=Totals(gross=Decimal("0"), payment_method="unknown"),
            meta={},
        )

    # Map to Invoice object
    merchant = Merchant(
        name=data.get("merchant_name", {}).get("value"),
        address=data.get("merchant_address", {}).get("value"),
    )

    items_data = data.get("menu", [])
    items = []
    for item_data in items_data:
        try:
            qty = Decimal(item_data.get("cnt", {}).get("value", "1"))
            unit_price = Decimal(item_data.get("price", {}).get("value", "0"))
            items.append(
                Item(
                    description=item_data.get("nm", {}).get("value"),
                    qty=qty,
                    unit_price=unit_price,
                    total_price=qty * unit_price,
                    vat_rate=19,  # Defaulting to 19, as the model doesn't provide this
                )
            )
        except (KeyError, TypeError, ValueError):
            continue

    totals = Totals(
        gross=Decimal(data.get("total", {}).get("price", {}).get("value", "0")),
        payment_method="unknown",
    )

    invoice = Invoice(
        invoice_id=str(uuid.uuid4()),
        merchant=merchant,
        timestamp="unknown",
        currency="EUR",
        items=items,
        totals=totals,
        meta={},
    )

    return invoice


def parse_text(ocr_text: str) -> Invoice:  # pragma: no cover
    """
    Optional stub if you choose to parse from pre-run OCR text.
    """
    raise NotImplementedError("parse_text() is not implemented yet")
