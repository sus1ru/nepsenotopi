from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Case, F, IntegerField, Sum, When
from rest_framework import serializers

from portfolio.models import PortfolioShare, Watchlist


class PortfolioShareSerializer(serializers.ModelSerializer):
    security_symbol = serializers.CharField(source='security.symbol', read_only=True)
    security_name = serializers.CharField(source='security.security_name', read_only=True)
    total_quantity = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioShare
        fields = (
            'id',
            'user',
            'security',
            'security_symbol',
            'security_name',
            'transaction_type',
            'share_value',
            'quantity',
            'total_quantity',
            'wacc',
            'date_created',
            'date_updated',
        )
        read_only_fields = (
            'id',
            'user',
            'security_symbol',
            'security_name',
            'total_quantity',
            'wacc',
            'date_created',
            'date_updated',
        )

    def validate(self, attrs):
        share_value = attrs.get(
            'share_value',
            getattr(self.instance, 'share_value', None),
        )
        quantity = attrs.get(
            'quantity',
            getattr(self.instance, 'quantity', None),
        )

        if share_value is not None and share_value <= 0:
            raise serializers.ValidationError(
                {'share_value': 'Share value must be greater than zero.'}
            )

        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError(
                {'quantity': 'Quantity must be greater than zero.'}
            )

        portfolio_share = self.instance or PortfolioShare()
        request = self.context.get('request')

        if portfolio_share.pk is None and request:
            portfolio_share.user = request.user

        for field in ('security', 'transaction_type', 'share_value', 'quantity'):
            if field in attrs:
                setattr(portfolio_share, field, attrs[field])

        try:
            portfolio_share.clean()
        except DjangoValidationError as exc:
            detail = exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
            raise serializers.ValidationError(detail)

        return attrs

    def get_total_quantity(self, obj):
        annotated_value = getattr(obj, 'total_quantity', None)
        if annotated_value is not None:
            return annotated_value

        return (
            PortfolioShare.objects
            .filter(
                user_id=obj.user_id,
                security_id=obj.security_id,
            )
            .aggregate(
                total=Sum(
                    Case(
                        When(transaction_type=PortfolioShare.SELL, then=-F('quantity')),
                        default=F('quantity'),
                        output_field=IntegerField(),
                    )
                )
            )['total']
            or 0
        )


class WatchlistSerializer(serializers.ModelSerializer):
    security_symbol = serializers.CharField(source='security.symbol', read_only=True)
    security_name = serializers.CharField(source='security.security_name', read_only=True)

    class Meta:
        model = Watchlist
        fields = (
            'id',
            'user',
            'security',
            'security_symbol',
            'security_name',
            'target_price',
            'alert_type',
            'is_active',
            'is_triggered',
            'triggered_at',
            'last_checked_price',
            'date_created',
            'date_updated',
        )
        read_only_fields = (
            'id',
            'user',
            'security_symbol',
            'security_name',
            'is_triggered',
            'triggered_at',
            'last_checked_price',
            'date_created',
            'date_updated',
        )
