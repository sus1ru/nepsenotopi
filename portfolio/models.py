from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from nepse.models import Security


class PortfolioShare(models.Model):
    BUY = 'buy'
    SELL = 'sell'
    TRANSACTION_TYPES = (
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_shares',
    )
    security = models.ForeignKey(
        Security,
        on_delete=models.CASCADE,
        related_name='portfolio_shares',
    )
    transaction_type = models.CharField(
        max_length=4,
        choices=TRANSACTION_TYPES,
        default=BUY,
    )
    share_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    wacc = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
    )
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['user', 'security'], name='portfolio_user_sec_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name='portfolio_quantity_gte_1',
            ),
            models.CheckConstraint(
                condition=models.Q(share_value__gte=Decimal('0.01')),
                name='portfolio_share_value_gte_001',
            ),
        ]

    def __str__(self):
        security = self.security.symbol or self.security.security_name or self.security_id
        return f'{self.user} - {security} {self.transaction_type} ({self.quantity})'

    @staticmethod
    def _quantize_wacc(value):
        return value.quantize(Decimal('0.01'))

    @classmethod
    def _calculate_waccs(cls, shares):
        total_cost = Decimal('0')
        total_quantity = 0
        calculated_waccs = {}

        for share in shares:
            if share.transaction_type == cls.SELL:
                if share.quantity > total_quantity:
                    security = share.security.symbol or share.security.security_name
                    raise ValidationError(
                        {
                            'quantity': (
                                f'Cannot sell {share.quantity} shares of {security}. '
                                f'Only {total_quantity} shares are available.'
                            )
                        }
                    )

                current_wacc = total_cost / total_quantity if total_quantity else Decimal('0')
                total_cost -= current_wacc * share.quantity
                total_quantity -= share.quantity
            else:
                total_cost += Decimal(str(share.share_value)) * share.quantity
                total_quantity += share.quantity

            if total_quantity:
                wacc = cls._quantize_wacc(total_cost / total_quantity)
            else:
                total_cost = Decimal('0')
                wacc = Decimal('0.00')

            calculated_waccs[share.pk] = wacc

        return calculated_waccs

    @classmethod
    def recalculate_waccs(cls, user_id, security_id):
        shares = list(
            cls.objects
            .filter(user_id=user_id, security_id=security_id)
            .order_by('date_created', 'id')
        )

        share_map = {share.pk: share for share in shares}
        for share_id, wacc in cls._calculate_waccs(shares).items():
            share = share_map[share_id]

            if share.wacc != wacc:
                cls.objects.filter(pk=share.pk).update(wacc=wacc)

    def clean(self):
        super().clean()

        if self.share_value is not None and self.share_value < Decimal('0.01'):
            raise ValidationError({'share_value': 'Share value must be greater than zero.'})

        if self.quantity is not None and self.quantity < 1:
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})

        if not self.user_id or not self.security_id:
            return

        shares = list(
            PortfolioShare.objects
            .filter(user_id=self.user_id, security_id=self.security_id)
            .order_by('date_created', 'id')
        )

        if self.pk:
            shares = [share for share in shares if share.pk != self.pk]

        shares.append(self)
        shares.sort(
            key=lambda share: (
                share.date_created is None,
                share.date_created,
                share.pk or 0,
            )
        )
        self._calculate_waccs(shares)

    def save(self, *args, **kwargs):
        previous_group = None
        if self.pk:
            previous_share = PortfolioShare.objects.get(pk=self.pk)
            previous_group = (previous_share.user_id, previous_share.security_id)

        self.wacc = Decimal('0')
        self.full_clean()
        super().save(*args, **kwargs)

        current_group = (self.user_id, self.security_id)
        if previous_group and previous_group != current_group:
            self.recalculate_waccs(*previous_group)
        self.recalculate_waccs(*current_group)
        self.wacc = PortfolioShare.objects.only('wacc').get(pk=self.pk).wacc


class Watchlist(models.Model):
    ABOVE = 'above'
    BELOW = 'below'
    ALERT_TYPES = (
        (ABOVE, 'Above or equal'),
        (BELOW, 'Below or equal'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watchlists',
    )
    security = models.ForeignKey(
        Security,
        on_delete=models.CASCADE,
        related_name='watchlists',
    )
    target_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    alert_type = models.CharField(
        max_length=8,
        choices=ALERT_TYPES,
        default=ABOVE,
    )
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    last_checked_price = models.DecimalField(
        max_digits=16,
        decimal_places=4,
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['user', 'security'], name='watchlist_user_sec_idx'),
            models.Index(fields=['is_active', 'is_triggered'], name='watchlist_alert_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(target_price__gte=Decimal('0.01')),
                name='watchlist_target_price_gte_001',
            ),
        ]

    def __str__(self):
        security = self.security.symbol or self.security.security_name or self.security_id
        return f'{self.user} - {security} {self.alert_type} {self.target_price}'

    def has_reached_target(self, price):
        if price is None:
            return False

        if self.alert_type == self.BELOW:
            return price <= self.target_price
        return price >= self.target_price
