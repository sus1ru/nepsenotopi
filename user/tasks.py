from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from user.utils import send_password_reset_email, send_verification_email


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_verification_email_task(self, user_id, site_url=None):
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return

    if user.email and not user.is_email_verified:
        send_verification_email(user, site_url=site_url)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_password_reset_email_task(self, user_id, site_url=None):
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return

    if user.email:
        send_password_reset_email(user, site_url=site_url)
