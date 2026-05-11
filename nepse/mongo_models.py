from datetime import datetime, timezone
from mongoengine import (
    Document,
    DateTimeField,
    StringField,
    IntField,
    EmailField,
    URLField,
    DecimalField,
    LazyReferenceField,
)


# ---------- BaseDocument ----------
class BaseDoc(Document):
    date_created = DateTimeField(
        default=lambda: datetime.now(timezone.utc), null=True, required=False
    )
    date_updated = DateTimeField(
        default=lambda: datetime.now(timezone.utc), null=True, required=False
    )

    meta = {
        "abstract": True,
        "db_alias": "nepsedb",
    }

    ACTIVE_STATUS = ("A", "I", "S", "D")
    BOOLEAN_CHOICES = ("Y", "N")


# ---------- Sector ----------
class SectorDoc(BaseDoc):
    id = IntField(primary_key=True)
    SECTORS = [
        "Commercial Banks",
        "Manufacturing And Processing",
        "Hotels And Tourism",
        "Others",
        "Hydro Power",
        "Tradings",
        "Non Life Insurance",
        "Development Banks",
        "Finance",
        "Microfinance",
        "Life Insurance",
        "Investment",
    ]

    sector_description = StringField(
        max_length=128, choices=SECTORS, unique=True, null=True, required=False
    )
    active_status = StringField(
        max_length=8, choices=BaseDoc.ACTIVE_STATUS, null=True, required=False
    )
    regulatory_body = StringField(max_length=128, null=True, required=False)

    meta = {
        "indexes": ["sector_description", "active_status"],
        "collection": "nepse_sector",
    }


# ---------- ShareGroup ----------
class ShareGroupDoc(BaseDoc):
    id = IntField(primary_key=True)
    SHARE_GROUPS = ["A", "Z", "B", "G"]

    name = StringField(
        max_length=16, choices=SHARE_GROUPS, unique=True, null=True, required=False
    )
    description = StringField(max_length=512, null=True, required=False)
    capital_range_min = IntField(null=True, required=False)
    is_default = StringField(
        max_length=8, choices=BaseDoc.BOOLEAN_CHOICES, null=True, required=False
    )
    active_status = StringField(
        max_length=8, choices=BaseDoc.ACTIVE_STATUS, null=True, required=False
    )

    meta = {"indexes": ["name", "active_status"], "collection": "nepse_sharegroup"}


# ---------- InstrumentType ----------
class InstrumentTypeDoc(BaseDoc):
    id = IntField(primary_key=True)
    INSTRUMENT_TYPES = [
        "Equity",
        "Mutual Funds",
        "Non-Convertible Debentures",
        "Preference Shares",
    ]
    INSTRUMENT_TYPE_CODES = ["EQ", "MF", "NCD", "PS"]

    code = StringField(
        max_length=8,
        choices=INSTRUMENT_TYPE_CODES,
        unique=True,
        null=True,
        required=False,
    )
    description = StringField(
        max_length=64, choices=INSTRUMENT_TYPES, unique=True, null=True, required=False
    )
    active_status = StringField(
        max_length=8, choices=BaseDoc.ACTIVE_STATUS, null=True, required=False
    )

    meta = {"indexes": ["code", "active_status"], "collection": "nepse_instrumenttype"}


# ---------- Security ----------
class SecurityDoc(BaseDoc):
    id = IntField(primary_key=True)
    symbol = StringField(max_length=16, unique=True, null=True, required=False)
    security_name = StringField(max_length=128, null=True, required=False)
    name = StringField(max_length=128, null=True, required=False)
    active_status = StringField(
        max_length=8, choices=BaseDoc.ACTIVE_STATUS, null=True, required=False
    )
    is_promoter = StringField(
        max_length=8, choices=BaseDoc.BOOLEAN_CHOICES, null=True, required=False
    )

    meta = {"indexes": ["symbol", "active_status"], "collection": "nepse_security"}


# ---------- Company ----------
class CompanyDoc(BaseDoc):
    id = IntField(primary_key=True)
    company_name = StringField(max_length=128, null=True, required=False)
    symbol = StringField(max_length=16, unique=True, null=True, required=False)
    security = LazyReferenceField(
        "SecurityDoc", reverse_delete_rule=0, null=True, required=False
    )
    security_id = IntField(null=True, required=False)
    active_status = StringField(
        max_length=8, choices=BaseDoc.ACTIVE_STATUS, null=True, required=False
    )
    company_email = EmailField(max_length=128, null=True, required=False)
    website = URLField(max_length=256, null=True, required=False)
    sector = LazyReferenceField(
        "SectorDoc", reverse_delete_rule=0, null=True, required=False
    )
    sector_id = IntField(null=True, required=False)
    instrument_type = LazyReferenceField(
        "InstrumentTypeDoc", reverse_delete_rule=0, null=True, required=False
    )
    instrument_type_id = IntField(null=True, required=False)

    meta = {"indexes": ["symbol", "active_status"], "collection": "nepse_company"}


# ---------- SecurityLog ----------
class SecurityLogDoc(BaseDoc):
    id = IntField(primary_key=True)
    business_date = DateTimeField(null=True, required=False)
    security = LazyReferenceField(
        "SecurityDoc", reverse_delete_rule=0, null=True, required=False
    )
    security_id = IntField(null=True, required=False)
    open_price = DecimalField(precision=4, null=True, required=False)
    high_price = DecimalField(precision=4, null=True, required=False)
    low_price = DecimalField(precision=4, null=True, required=False)
    close_price = DecimalField(precision=4, null=True, required=False)
    total_traded_quantity = IntField(null=True, required=False)
    total_traded_value = DecimalField(precision=4, null=True, required=False)
    previous_day_close_price = DecimalField(precision=4, null=True, required=False)
    fifty_two_week_high = DecimalField(precision=4, null=True, required=False)
    fifty_two_week_low = DecimalField(precision=4, null=True, required=False)
    last_updated_time = DateTimeField(null=True, required=False)
    last_updated_price = DecimalField(precision=4, null=True, required=False)
    total_trades = IntField(null=True, required=False)
    average_traded_price = DecimalField(precision=4, null=True, required=False)
    market_capitalization = DecimalField(precision=4, null=True, required=False)

    meta = {"indexes": ["business_date", "security"], "collection": "nepse_securitylog"}
