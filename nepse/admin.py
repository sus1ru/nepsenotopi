from django.contrib import admin

from nepse.models import (
    Company,
    InstrumentType,
    Sector,
    Security,
    SecurityLog,
    ShareGroup,
)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = (
        "sector_description",
        "active_status",
        "regulatory_body",
        "date_created",
        "date_updated",
    )
    search_fields = ("sector_description", "regulatory_body")
    list_filter = ("active_status", "sector_description")
    ordering = ("sector_description",)


@admin.register(ShareGroup)
class ShareGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "capital_range_min",
        "is_default",
        "active_status",
        "date_created",
    )
    search_fields = ("name", "description")
    list_filter = ("name", "is_default", "active_status")
    ordering = ("name",)


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "security_name",
        "name",
        "active_status",
        "is_promoter",
        "date_created",
    )
    search_fields = ("symbol", "security_name", "name")
    list_filter = ("active_status", "is_promoter")
    ordering = ("symbol",)


@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "active_status", "date_created")
    search_fields = ("code", "description")
    list_filter = ("active_status",)
    ordering = ("code",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "company_name",
        "security",
        "sector",
        "instrument_type",
        "active_status",
        "company_email",
        "website",
    )
    search_fields = (
        "symbol",
        "company_name",
        "company_email",
        "security__symbol",
        "sector__sector_description",
        "instrument_type__code",
    )
    list_filter = ("active_status", "sector", "instrument_type")
    autocomplete_fields = ("security", "sector", "instrument_type")
    ordering = ("symbol",)


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = (
        "security__symbol",
        "business_date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "total_traded_quantity",
        "total_trades",
        "last_updated_time",
    )
    search_fields = ("security__symbol", "security__security_name")
    list_filter = ("business_date",)
    autocomplete_fields = ("security",)
    ordering = ("-business_date",)
    date_hierarchy = "business_date"
