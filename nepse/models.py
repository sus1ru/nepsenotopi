from django.db import models


class BaseModel(models.Model):
    ACTIVE_STATUS = [
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('S', 'Suspended'),
        ('D', 'Delisted'),
    ]
    BOOLEAN_CHOICES = [
        ('Y', 'true'),
        ('N', 'false'),
    ]
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class Sector(BaseModel):
    SECTORS = [
        ('Commercial Banks', 'Commercial Banks'),
        ('Manufacturing And Processing', 'Manufacturing And Processing'),
        ('Hotels And Tourism', 'Hotels And Tourism'),
        ('Others', 'Others'),
        ('Hydro Power', 'Hydro Power'),
        ('Tradings', 'Tradings'),
        ('Non Life Insurance', 'Non Life Insurance'),
        ('Development Banks', 'Development Banks'),
        ('Finance', 'Finance'),
        ('Microfinance', 'Microfinance'),
        ('Life Insurance', 'Life Insurance'),
        ('Investment', 'Investment'),
    ]

    sector_description = models.CharField(
        max_length=128, unique=True,
        choices=SECTORS,
        null=True, blank=True
    )
    active_status = models.CharField(
        max_length=8,
        choices=BaseModel.ACTIVE_STATUS,
        null=True, blank=True
    )
    regulatory_body = models.CharField(max_length=128, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(
                fields=['sector_description', 'active_status'],
                name='sector_name_idx'
            ),
        ]


class ShareGroup(BaseModel):
    SHARE_GROUPS = [
        ('A', 'A'),
        ('Z', 'Z'),
        ('B', 'B'),
        ('G', 'G'),
    ]

    name = models.CharField(
        max_length=16, unique=True,
        choices=SHARE_GROUPS,
        null=True, blank=True
    )
    description = models.CharField(max_length=512, null=True, blank=True)
    capital_range_min = models.IntegerField(null=True, blank=True)
    is_default = models.CharField(
        max_length=8,
        choices=BaseModel.BOOLEAN_CHOICES,
        null=True, blank=True
    )
    active_status = models.CharField(
        max_length=8,
        choices=BaseModel.ACTIVE_STATUS,
        null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['name', 'active_status'],
                name='share_group_name_idx'
            ),
        ]


class Security(BaseModel):
    symbol = models.CharField(
        max_length=16, unique=True,
        null=True, blank=True
    )
    security_name = models.CharField(max_length=128, null=True, blank=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    active_status = models.CharField(
        max_length=8,
        choices=BaseModel.ACTIVE_STATUS,
        null=True, blank=True
    )
    is_promoter = models.CharField(
        max_length=8,
        choices=BaseModel.BOOLEAN_CHOICES,
        null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['symbol', 'active_status'],
                name='security_symbol_idx'
            ),
        ]


class InstrumentType(BaseModel):
    INSTRUMENT_TYPES = [
        ('Equity', 'Equity'),
        ('Mutual Funds', 'Mutual Funds'),
        ('Non-Convertible Debentures', 'Non-Convertible Debentures'),
        ('Preference Shares', 'Preference Shares'),
    ]
    INSTRUMENT_TYPE_CODES = [
        ('EQ', 'Equity'),
        ('MF', 'Mutual Funds'),
        ('NCD', 'Non-Convertible Debentures'),
        ('PS', 'Preference Shares'),
    ]
    code = models.CharField(
        max_length=8, unique=True,
        choices=INSTRUMENT_TYPE_CODES,
        null=True, blank=True
    )
    description = models.CharField(
        max_length=64, unique=True,
        choices=INSTRUMENT_TYPES,
        null=True, blank=True
    )
    active_status = models.CharField(
        max_length=8,
        choices=BaseModel.ACTIVE_STATUS,
        null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['code', 'active_status'],
                name='instrument_type_code_idx'
            ),
        ]


class Company(BaseModel):
    company_name = models.CharField(max_length=128, null=True, blank=True)
    symbol = models.CharField(
        max_length=16, unique=True,
        null=True, blank=True
    )
    security = models.OneToOneField(
        'nepse.Security',
        related_name='company',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    active_status = models.CharField(
        max_length=8,
        choices=BaseModel.ACTIVE_STATUS,
        null=True, blank=True
    )
    company_email = models.EmailField(max_length=128, null=True, blank=True)
    website = models.URLField(max_length=256, null=True, blank=True)
    sector = models.ForeignKey(
        'nepse.Sector',
        related_name='companies',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    instrument_type = models.ForeignKey(
        'nepse.InstrumentType',
        related_name='companies',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['symbol', 'active_status'],
                name='company_symbol_idx'
            ),
        ]


class SecurityLog(BaseModel):
    business_date = models.DateTimeField(blank=True, null=True)
    security = models.ForeignKey(
        'nepse.Security',
        related_name='security_logs',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    open_price = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    high_price = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    low_price = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    close_price = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    total_traded_quantity = models.IntegerField(blank=True, null=True)
    total_traded_value = models.DecimalField(
        max_digits=32, decimal_places=4,
        blank=True, null=True
    )
    previous_day_close_price = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    fifty_two_week_high = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    fifty_two_week_low = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    last_updated_time = models.DateTimeField(blank=True, null=True)
    last_updated_price = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    total_trades = models.IntegerField(blank=True, null=True)
    average_traded_price = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )
    market_capitalization = models.DecimalField(
        max_digits=16, decimal_places=4,
        blank=True, null=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['business_date', 'security'],
                name='security_log_idx'
            ),
        ]
