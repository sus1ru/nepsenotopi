from django.db.models import Case, F, IntegerField, OuterRef, Q, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from portfolio.models import PortfolioShare, Watchlist
from portfolio.paginations import PortfolioPagination
from portfolio.serializers import PortfolioShareSerializer, WatchlistSerializer


def annotate_total_quantity(queryset, user):
    return queryset.annotate(
        total_quantity=Coalesce(
            Sum(
                Case(
                    When(
                        security__portfolio_shares__transaction_type=PortfolioShare.SELL,
                        then=-F('security__portfolio_shares__quantity'),
                    ),
                    default=F('security__portfolio_shares__quantity'),
                    output_field=IntegerField(),
                ),
                filter=Q(security__portfolio_shares__user=user),
            ),
            Value(0),
            output_field=IntegerField(),
        )
    )


class PortfolioShareViewSet(ModelViewSet):
    serializer_class = PortfolioShareSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PortfolioPagination
    filterset_fields = ('security', 'security__symbol', 'transaction_type')
    search_fields = ('security__symbol', 'security__security_name')
    ordering_fields = (
        'id',
        'security_id',
        'security__symbol',
        'transaction_type',
        'share_value',
        'quantity',
        'total_quantity',
        'wacc',
        'date_created',
        'date_updated',
    )
    ordering = ('-date_created',)

    def get_queryset(self):
        return (
            annotate_total_quantity(
                PortfolioShare.objects
                .select_related('user', 'security')
                .filter(user=self.request.user),
                self.request.user,
            )
            .order_by('-date_created')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LatestPortfolioShareWaccViewSet(ReadOnlyModelViewSet):
    serializer_class = PortfolioShareSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PortfolioPagination
    filterset_fields = ('security', 'security__symbol', 'transaction_type')
    search_fields = ('security__symbol', 'security__security_name')
    ordering_fields = (
        'id',
        'security_id',
        'security__symbol',
        'transaction_type',
        'share_value',
        'quantity',
        'total_quantity',
        'wacc',
        'date_created',
        'date_updated',
    )
    ordering = ('security__symbol',)

    def get_queryset(self):
        latest_share_ids = (
            PortfolioShare.objects
            .filter(
                user=self.request.user,
                security_id=OuterRef('security_id'),
            )
            .order_by('-date_created', '-id')
            .values('id')[:1]
        )

        return (
            annotate_total_quantity(
                PortfolioShare.objects
                .select_related('user', 'security')
                .filter(
                    user=self.request.user,
                    id=Subquery(latest_share_ids),
                ),
                self.request.user,
            )
            .order_by('security__symbol')
        )


class WatchlistViewSet(ModelViewSet):
    serializer_class = WatchlistSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PortfolioPagination
    filterset_fields = ('security', 'security__symbol', 'alert_type', 'is_active', 'is_triggered')
    search_fields = ('security__symbol', 'security__security_name')
    ordering_fields = (
        'id',
        'security__symbol',
        'target_price',
        'last_checked_price',
        'triggered_at',
        'date_created',
        'date_updated',
    )
    ordering = ('-date_created',)

    def get_queryset(self):
        return (
            Watchlist.objects
            .select_related('user', 'security')
            .filter(user=self.request.user)
            .order_by('-date_created')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
