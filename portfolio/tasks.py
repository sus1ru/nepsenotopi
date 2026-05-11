from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from nepse.models import SecurityLog
from portfolio.models import Watchlist


def _latest_price_for_security(security_id):
    security_log = (
        SecurityLog.objects
        .filter(security_id=security_id)
        .exclude(last_updated_price__isnull=True, close_price__isnull=True)
        .order_by('-business_date', '-last_updated_time', '-date_created', '-id')
        .first()
    )
    if not security_log:
        return None

    return security_log.last_updated_price or security_log.close_price


def _send_watchlist_email(watchlist, current_price):
    security = watchlist.security.symbol or watchlist.security.security_name
    send_mail(
        subject=f'{security} reached your watchlist target',
        message=(
            f'{security} reached your {watchlist.alert_type} target of '
            f'{watchlist.target_price}. Current price: {current_price}.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[watchlist.user.email],
        fail_silently=False,
    )


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def check_watchlist_alerts(self):
    watchlists = (
        Watchlist.objects
        .select_related('user', 'security')
        .filter(is_active=True, is_triggered=False, user__email__gt='')
    )

    for watchlist in watchlists:
        current_price = _latest_price_for_security(watchlist.security_id)
        if current_price is None:
            continue

        watchlist.last_checked_price = current_price
        if not watchlist.has_reached_target(current_price):
            watchlist.save(update_fields=['last_checked_price', 'date_updated'])
            continue

        with transaction.atomic():
            locked_watchlist = (
                Watchlist.objects
                .select_for_update()
                .select_related('user', 'security')
                .get(pk=watchlist.pk)
            )
            if locked_watchlist.is_triggered:
                continue

            _send_watchlist_email(locked_watchlist, current_price)
            locked_watchlist.last_checked_price = current_price
            locked_watchlist.is_triggered = True
            locked_watchlist.is_active = False
            locked_watchlist.triggered_at = timezone.now()
            locked_watchlist.save(
                update_fields=[
                    'last_checked_price',
                    'is_triggered',
                    'is_active',
                    'triggered_at',
                    'date_updated',
                ]
            )
