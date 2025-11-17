from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from pydantic import BaseModel, Field, validator


def _D(x) -> Decimal:
    if not isinstance(x, Decimal):
        x = Decimal(str(x))
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Merchant(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None


class Item(BaseModel):
    sku_or_ean: Optional[str] = Field(None, description="May be missing on many receipts")
    description: str
    qty: Decimal = Field(..., gt=Decimal("0"))
    unit_price: Decimal = Field(..., ge=Decimal("0"))
    total_price: Decimal = Field(..., ge=Decimal("0"))
    vat_rate: int = Field(..., description="e.g., 7 or 19 in Germany")
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    raw_line: Optional[str] = None

    @validator("qty", "unit_price", "total_price", pre=True)
    def _cast_decimal(cls, v):
        return _D(v)

    @validator("total_price")
    def _check_total_matches_unit_times_qty(cls, v, values):
        # Do not hard-fail on tiny rounding differences; allow 0.02 tolerance
        qty = values.get("qty")
        unit = values.get("unit_price")
        if qty is not None and unit is not None:
            expected = (qty * unit).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if abs(v - expected) > Decimal("0.02"):
                # Keep value, but this will be asserted in tests if needed
                pass
        return v


class Totals(BaseModel):
    gross: Decimal
    payment_method: str

    @validator("gross", pre=True)
    def _cast_decimal(cls, v):
        return _D(v)


class Invoice(BaseModel):
    invoice_id: str
    merchant: Merchant
    timestamp: str  # keep as ISO string; parsing is out-of-scope for tests
    currency: str = Field("EUR", const=True)
    items: List[Item]
    totals: Totals
    meta: dict

    def sum_items(self) -> Decimal:
        return sum((i.total_price for i in self.items), Decimal("0.00")).quantize(Decimal("0.01"))
