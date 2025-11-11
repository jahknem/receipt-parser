from decimal import Decimal
from receipt_reader.types import Invoice, Merchant, Item, Totals

# NOTE: These values are derived from the user's provided photos and represent legal, test-ready data.

TOOM = Invoice(
    invoice_id="toom-2025-08-05-170907",
    merchant=Merchant(
        name="toom Baumarkt GmbH",
        address="Straßheimerstraße 27, 61169 Friedberg",
        phone="06031/735130",
    ),
    timestamp="2025-08-05T17:09:07",
    currency="EUR",
    items=[
        Item(sku_or_ean="4002718777225", description="Winkelleiste Kiefer", qty=1, unit_price=13.99, total_price=13.99, vat_rate=19, confidence=0.98,
             raw_line="4002718777225 Winkelleiste Kie 13.99 19"),
        Item(sku_or_ean="4002718787125", description="Winkelleiste", qty=1, unit_price=6.99, total_price=6.99, vat_rate=19, confidence=0.98,
             raw_line="4002718787125 Winkelleiste 6.99 19"),
        Item(sku_or_ean="4051281464537", description="Solarleuchte", qty=3, unit_price=2.99, total_price=8.97, vat_rate=19, confidence=0.95,
             raw_line="3.000 STK a 2.99 8.97 19"),
        Item(sku_or_ean="4011261097018", description="Carnivoren Sonne", qty=1, unit_price=5.99, total_price=5.99, vat_rate=7, confidence=0.92,
             raw_line="4011261097018 CARNIVOREN SONNE 5.99 7"),
        Item(sku_or_ean="4337256024624", description="Luftverbesserer", qty=1, unit_price=27.99, total_price=27.99, vat_rate=7, confidence=0.92,
             raw_line="4337256024624 LUFTVERBESSERER 27.99 7"),
        Item(sku_or_ean="00000000400325", description="Übertopf 18x15c", qty=1, unit_price=12.99, total_price=12.99, vat_rate=19, confidence=0.96,
             raw_line="00000000400325 Uebertopf 18x15c 12.99 19"),
        Item(sku_or_ean="4002718778871", description="Rundstab Kiefer", qty=1, unit_price=2.49, total_price=2.49, vat_rate=19, confidence=0.98,
             raw_line="4002718778871 Rundstab Kiefer 2.49 19"),
    ],
    totals=Totals(gross=Decimal("79.41"), payment_method="VISA (contactless, Visa Debit)"),
    meta={"source_image": "tests/toom.png", "notes": None},
)

TEGUT = Invoice(
    invoice_id="tegut-2021-03-15",
    merchant=Merchant(
        name="tegut",
        address="Fauerbacher Str. 9, 61169 Friedberg",
        phone="06031/1699770",
    ),
    timestamp="2021-03-15T00:00:00",
    currency="EUR",
    items=[
        Item(sku_or_ean=None, description="Tragetasche", qty=1, unit_price=0.20, total_price=0.20, vat_rate=19, confidence=0.9,
             raw_line="Tragetasche 0.20"),
        Item(sku_or_ean=None, description="BIO Mayka Chips", qty=3, unit_price=1.79, total_price=5.37, vat_rate=7, confidence=0.96,
             raw_line="BIO Mayka Chips 1.79 (three lines)"),
        Item(sku_or_ean=None, description="Hitschler XXL Fruchtgummi", qty=2, unit_price=1.29, total_price=2.58, vat_rate=7, confidence=0.94,
             raw_line="Hitschler XXL Fruchtgummi 1.29 (two lines)"),
    ],
    totals=Totals(gross=Decimal("8.15"), payment_method="SEPA-ELV"),
    meta={"source_image": "tests/tegut.png", "notes": None},
)

JACQUES = Invoice(
    invoice_id="jacques-2025-08-07-1748",
    merchant=Merchant(
        name="Jacques’ Wein-Depot 230",
        address="Frankfurter Straße 45, 61231 Bad Nauheim",
        phone="06032/349338",
    ),
    timestamp="2025-08-07T17:48:00",
    currency="EUR",
    items=[
        Item(sku_or_ean="K2722", description="Manufaktur Geiger, Pomaria", qty=6, unit_price=10.20, total_price=61.20, vat_rate=19, confidence=0.7,
             raw_line="6x MANUFAKTUR GEIGER Pomaria / Summe 61,20"),
    ],
    totals=Totals(gross=Decimal("61.20"), payment_method="Visa Debit (contactless)"),
    meta={"source_image": "tests/jacques.png", "notes": "Unit price derived from total/qty."},
)

REWE_2025_08_08 = Invoice(
    invoice_id="rewe-2025-08-08-1524",
    merchant=Merchant(
        name="REWE – Im Krämer",
        address="61169 Friedberg",
        phone="06031-1667168",
    ),
    timestamp="2025-08-08T15:24:12",
    currency="EUR",
    items=[
        Item(sku_or_ean=None, description="Maki Gurke (X01 – Eat Happy)", qty=1, unit_price=3.99, total_price=3.99, vat_rate=7, confidence=0.98,
             raw_line="MAKI GURKE X01 3,99 B"),
        Item(sku_or_ean=None, description="Maki Avocado (X01 – Eat Happy)", qty=1, unit_price=4.49, total_price=4.49, vat_rate=7, confidence=0.98,
             raw_line="MAKI AVOCADO X01 4,49 B"),
        Item(sku_or_ean=None, description="Bio Eier (Kl. M–L)", qty=1, unit_price=4.99, total_price=4.99, vat_rate=7, confidence=0.6,
             raw_line="BIO EI KL. M-L 4,99 B"),
        Item(sku_or_ean=None, description="Bio Crème Fraîche", qty=3, unit_price=1.19, total_price=3.57, vat_rate=7, confidence=0.9,
             raw_line="3 Stk x 1,19 = 3,57 B"),
        Item(sku_or_ean=None, description="Dinkelmehl T630", qty=1, unit_price=1.39, total_price=1.39, vat_rate=7, confidence=0.85,
             raw_line="DINKELMEHL T630 1,39 B"),
        Item(sku_or_ean=None, description="Blockschokolade", qty=2, unit_price=2.99, total_price=5.98, vat_rate=7, confidence=0.85,
             raw_line="2 Stk x 2,99 = 5,98 B"),
        Item(sku_or_ean=None, description="Kidney Bohnen", qty=2, unit_price=2.39, total_price=4.78, vat_rate=7, confidence=0.9,
             raw_line="2 Stk x 2,39 = 4,78 B"),
        Item(sku_or_ean=None, description="Bio Passata", qty=1, unit_price=1.59, total_price=1.59, vat_rate=7, confidence=0.9,
             raw_line="BIO PASSATA 1,59 B"),
        Item(sku_or_ean=None, description="Schaschlikspieß", qty=1, unit_price=1.99, total_price=1.99, vat_rate=19, confidence=0.6,
             raw_line="…SPIESS 1,99 A"),
    ],
     totals=Totals(gross=Decimal("32.77"), payment_method="Debit Mastercard (contactless)"),
    meta={"source_image": "tests/rewe.png", "notes": None},
)

REWE_2025_08_07 = Invoice(
    invoice_id="rewe-2025-08-07-2102",
    merchant=Merchant(
        name="REWE – Im Krämer",
        address="61169 Friedberg",
        phone="06031-1667168",
    ),
    timestamp="2025-08-07T21:02:00",
    currency="EUR",
    items=[
        Item(sku_or_ean=None, description="Kartoffeln VF Bio", qty=1, unit_price=2.29, total_price=2.29, vat_rate=7, confidence=0.95,
             raw_line="KART.VF.BIO 2,29 B"),
        Item(sku_or_ean=None, description="Pizza Speciale", qty=1, unit_price=3.49, total_price=3.49, vat_rate=7, confidence=0.98,
             raw_line="PIZZA SPECIALE 3,49 B"),
        Item(sku_or_ean=None, description="Pizza Vegetale", qty=1, unit_price=3.49, total_price=3.49, vat_rate=7, confidence=0.98,
             raw_line="PIZZA VEGETALE 3,49 B"),
        Item(sku_or_ean=None, description="TOIPA 3LG NATECO (non-food)", qty=1, unit_price=2.99, total_price=2.99, vat_rate=19, confidence=0.85,
             raw_line="TOIPA 3LG NATECO 2,99 A"),
    ],
    totals=Totals(gross=Decimal("12.26"), payment_method="Cash (20.00 given, 7.74 change)"),
    meta={"source_image": "tests/rewe2.png", "notes": None},
)

ALL_FIXTURES = [TOOM, TEGUT, JACQUES, REWE_2025_08_08, REWE_2025_08_07]
