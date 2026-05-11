from rest_framework.viewsets import ReadOnlyModelViewSet

from nepse.filters import (
    CompanyFilter,
    InstrumentTypeFilter,
    SecurityFilter,
    SecurityLogFilter,
    SectorFilter,
    ShareGroupFilter,
)
from nepse.models import (
    Company,
    InstrumentType,
    Security,
    SecurityLog,
    Sector,
    ShareGroup,
)
from nepse.serializers import (
    CompanySerializer,
    InstrumentTypeSerializer,
    SecurityLogSerializer,
    SecuritySerializer,
    SectorSerializer,
    ShareGroupSerializer,
)
from nepse.paginations import (
    CompanyPagination,
    SecurityLogPagination,
    SecurityPagination,
    SmallLookupPagination,
)


class SectorViewSet(ReadOnlyModelViewSet):
    queryset = Sector.objects.all().order_by('sector_description')
    serializer_class = SectorSerializer
    filterset_class = SectorFilter
    pagination_class = SmallLookupPagination
    search_fields = ['sector_description', 'regulatory_body', 'active_status']
    ordering_fields = ['id', 'sector_description', 'regulatory_body', 'active_status', 'date_created', 'date_updated']
    ordering = ['sector_description']


class ShareGroupViewSet(ReadOnlyModelViewSet):
    queryset = ShareGroup.objects.all().order_by('name')
    serializer_class = ShareGroupSerializer
    filterset_class = ShareGroupFilter
    pagination_class = SmallLookupPagination
    search_fields = ['name', 'description', 'active_status', 'is_default']
    ordering_fields = ['id', 'name', 'capital_range_min', 'active_status', 'date_created', 'date_updated']
    ordering = ['name']


class SecurityViewSet(ReadOnlyModelViewSet):
    queryset = Security.objects.all().order_by('symbol')
    serializer_class = SecuritySerializer
    filterset_class = SecurityFilter
    pagination_class = SecurityPagination
    search_fields = ['symbol', 'security_name', 'name', 'active_status']
    ordering_fields = ['id', 'symbol', 'security_name', 'name', 'active_status', 'date_created', 'date_updated']
    ordering = ['symbol']


class InstrumentTypeViewSet(ReadOnlyModelViewSet):
    queryset = InstrumentType.objects.all().order_by('code')
    serializer_class = InstrumentTypeSerializer
    filterset_class = InstrumentTypeFilter
    pagination_class = SmallLookupPagination
    search_fields = ['code', 'description', 'active_status']
    ordering_fields = ['id', 'code', 'description', 'active_status', 'date_created', 'date_updated']
    ordering = ['code']


class CompanyViewSet(ReadOnlyModelViewSet):
    queryset = Company.objects.select_related(
        'sector',
        'instrument_type',
        'security',
    ).all().order_by('symbol')
    serializer_class = CompanySerializer
    filterset_class = CompanyFilter
    pagination_class = CompanyPagination
    search_fields = [
        'company_name',
        'symbol',
        'company_email',
        'website',
        'sector__sector_description',
        'instrument_type__code',
        'security__symbol',
    ]
    ordering_fields = ['id', 'company_name', 'symbol', 'active_status', 'date_created', 'date_updated']
    ordering = ['symbol']


class SecurityLogViewSet(ReadOnlyModelViewSet):
    queryset = SecurityLog.objects.select_related('security').all().order_by('-business_date', 'security__symbol')
    serializer_class = SecurityLogSerializer
    filterset_class = SecurityLogFilter
    pagination_class = SecurityLogPagination
    search_fields = ['security__symbol']
    ordering_fields = [
        'id',
        'business_date',
        'security__symbol',
        'open_price',
        'high_price',
        'low_price',
        'close_price',
        'total_traded_quantity',
        'total_traded_value',
        'total_trades',
        'market_capitalization',
        'date_created',
        'date_updated',
    ]
    ordering = ['-business_date', 'security__symbol']
