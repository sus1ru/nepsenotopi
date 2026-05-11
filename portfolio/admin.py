from django.contrib import admin

from portfolio.models import PortfolioShare, Watchlist


@admin.register(PortfolioShare)
class PortfolioShareAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'security',
        'transaction_type',
        'share_value',
        'quantity',
        'wacc',
        'date_created',
    )
    list_filter = ('transaction_type', 'security')
    search_fields = (
        'user__email',
        'user__username',
        'security__symbol',
        'security__security_name',
    )
    autocomplete_fields = ('user', 'security')
    readonly_fields = ('wacc', 'date_created', 'date_updated')
    ordering = ('-date_created',)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'security',
        'target_price',
        'alert_type',
        'is_active',
        'is_triggered',
        'last_checked_price',
        'triggered_at',
    )
    list_filter = ('alert_type', 'is_active', 'is_triggered', 'security')
    search_fields = (
        'user__email',
        'user__username',
        'security__symbol',
        'security__security_name',
    )
    autocomplete_fields = ('user', 'security')
    readonly_fields = ('last_checked_price', 'triggered_at', 'date_created', 'date_updated')
    ordering = ('-date_created',)
