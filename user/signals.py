from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.tasks import send_verification_email_task


User = get_user_model()


@receiver(post_save, sender=User)
def send_verification_email_on_user_create(sender, instance, created, **kwargs):
    if not created or not instance.email or instance.is_email_verified or instance.is_superuser:
        return

    send_verification_email_task.delay(instance.pk, settings.SITE_URL)
