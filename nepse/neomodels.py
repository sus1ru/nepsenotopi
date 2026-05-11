from neomodel import (
    DateTimeProperty,
    FloatProperty,
    IntegerProperty,
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    ZeroOrMore,
    ZeroOrOne,
)


class BaseNeoModel(StructuredNode):
    __abstract_node__ = True

    # Stable link back to the relational row for ETL and sync jobs.
    django_id = IntegerProperty(unique_index=True, required=True)
    date_created = DateTimeProperty()
    date_updated = DateTimeProperty()


class SectorNode(BaseNeoModel):
    sector_description = StringProperty(unique_index=True)
    active_status = StringProperty(index=True)
    regulatory_body = StringProperty(index=True)

    companies = RelationshipFrom(
        'CompanyNode',
        'BELONGS_TO_SECTOR',
        cardinality=ZeroOrMore,
    )


class ShareGroupNode(BaseNeoModel):
    name = StringProperty(unique_index=True)
    description = StringProperty()
    capital_range_min = IntegerProperty(index=True)
    is_default = StringProperty(index=True)
    active_status = StringProperty(index=True)


class SecurityNode(BaseNeoModel):
    symbol = StringProperty(unique_index=True)
    security_name = StringProperty(index=True)
    name = StringProperty(index=True)
    active_status = StringProperty(index=True)
    is_promoter = StringProperty(index=True)

    company = RelationshipFrom(
        'CompanyNode',
        'REPRESENTS_SECURITY',
        cardinality=ZeroOrOne,
    )
    security_logs = RelationshipFrom(
        'SecurityLogNode',
        'LOGS_SECURITY',
        cardinality=ZeroOrMore,
    )


class InstrumentTypeNode(BaseNeoModel):
    code = StringProperty(unique_index=True)
    description = StringProperty(unique_index=True)
    active_status = StringProperty(index=True)

    companies = RelationshipFrom(
        'CompanyNode',
        'HAS_INSTRUMENT_TYPE',
        cardinality=ZeroOrMore,
    )


class CompanyNode(BaseNeoModel):
    company_name = StringProperty(index=True)
    symbol = StringProperty(unique_index=True)
    active_status = StringProperty(index=True)
    company_email = StringProperty(index=True)
    website = StringProperty()

    security = RelationshipTo(
        'SecurityNode',
        'REPRESENTS_SECURITY',
        cardinality=ZeroOrOne,
    )
    sector = RelationshipTo(
        'SectorNode',
        'BELONGS_TO_SECTOR',
        cardinality=ZeroOrOne,
    )
    instrument_type = RelationshipTo(
        'InstrumentTypeNode',
        'HAS_INSTRUMENT_TYPE',
        cardinality=ZeroOrOne,
    )


class SecurityLogNode(BaseNeoModel):
    business_date = DateTimeProperty(index=True)
    open_price = FloatProperty()
    high_price = FloatProperty()
    low_price = FloatProperty()
    close_price = FloatProperty()
    total_traded_quantity = IntegerProperty(index=True)
    total_traded_value = FloatProperty()
    previous_day_close_price = FloatProperty()
    fifty_two_week_high = FloatProperty()
    fifty_two_week_low = FloatProperty()
    last_updated_time = DateTimeProperty(index=True)
    last_updated_price = FloatProperty()
    total_trades = IntegerProperty(index=True)
    average_traded_price = FloatProperty()
    market_capitalization = FloatProperty(index=True)

    security = RelationshipTo(
        'SecurityNode',
        'LOGS_SECURITY',
        cardinality=One,
    )
