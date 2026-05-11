import django_filters

from nepse.models import (
    Company,
    InstrumentType,
    Security,
    SecurityLog,
    Sector,
    ShareGroup,
)


class SectorFilter(django_filters.FilterSet):
    sector_description = django_filters.CharFilter(lookup_expr='icontains')
    regulatory_body = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Sector
        fields = ['active_status', 'sector_description', 'regulatory_body']


class ShareGroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')
    description = django_filters.CharFilter(lookup_expr='icontains')
    capital_range_min = django_filters.RangeFilter()

    class Meta:
        model = ShareGroup
        fields = ['name', 'active_status', 'is_default', 'capital_range_min']


class SecurityFilter(django_filters.FilterSet):
    symbol = django_filters.CharFilter(lookup_expr='icontains')
    security_name = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Security
        fields = ['symbol', 'security_name', 'name', 'active_status', 'is_promoter']


class InstrumentTypeFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr='iexact')
    description = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = InstrumentType
        fields = ['code', 'description', 'active_status']


class CompanyFilter(django_filters.FilterSet):
    company_name = django_filters.CharFilter(lookup_expr='icontains')
    symbol = django_filters.CharFilter(lookup_expr='icontains')
    company_email = django_filters.CharFilter(lookup_expr='icontains')
    website = django_filters.CharFilter(lookup_expr='icontains')
    sector = django_filters.NumberFilter(field_name='sector_id')
    instrument_type = django_filters.NumberFilter(field_name='instrument_type_id')
    security = django_filters.NumberFilter(field_name='security_id')
    sector_description = django_filters.CharFilter(
        field_name='sector__sector_description',
        lookup_expr='icontains'
    )
    instrument_type_code = django_filters.CharFilter(
        field_name='instrument_type__code',
        lookup_expr='iexact'
    )
    security_symbol = django_filters.CharFilter(
        field_name='security__symbol',
        lookup_expr='icontains'
    )

    class Meta:
        model = Company
        fields = [
            'company_name',
            'symbol',
            'active_status',
            'company_email',
            'website',
            'sector',
            'instrument_type',
            'security',
            'sector_description',
            'instrument_type_code',
            'security_symbol',
        ]


class SecurityLogFilter(django_filters.FilterSet):
    business_date = django_filters.DateTimeFromToRangeFilter()
    last_updated_time = django_filters.DateTimeFromToRangeFilter()
    security = django_filters.NumberFilter(field_name='security_id')
    security_symbol = django_filters.CharFilter(
        field_name='security__symbol',
        lookup_expr='icontains'
    )
    open_price = django_filters.RangeFilter()
    high_price = django_filters.RangeFilter()
    low_price = django_filters.RangeFilter()
    close_price = django_filters.RangeFilter()
    total_traded_quantity = django_filters.RangeFilter()
    total_traded_value = django_filters.RangeFilter()
    previous_day_close_price = django_filters.RangeFilter()
    fifty_two_week_high = django_filters.RangeFilter()
    fifty_two_week_low = django_filters.RangeFilter()
    last_updated_price = django_filters.RangeFilter()
    total_trades = django_filters.RangeFilter()
    average_traded_price = django_filters.RangeFilter()
    market_capitalization = django_filters.RangeFilter()

    class Meta:
        model = SecurityLog
        fields = [
            'business_date',
            'security',
            'security_symbol',
            'last_updated_time',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'total_traded_quantity',
            'total_traded_value',
            'previous_day_close_price',
            'fifty_two_week_high',
            'fifty_two_week_low',
            'last_updated_price',
            'total_trades',
            'average_traded_price',
            'market_capitalization',
        ]
