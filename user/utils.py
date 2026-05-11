from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from urllib.parse import urljoin


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.password}{user.is_email_verified}"


email_verification_token_generator = EmailVerificationTokenGenerator()


def _uid_for_user(user):
    return urlsafe_base64_encode(force_bytes(user.pk))


def get_request_base_url(request):
    return request.build_absolute_uri("/").rstrip("/")


def _build_absolute_uri(view_name, *, request=None, site_url=None, **kwargs):
    path = reverse(view_name, kwargs=kwargs)
    if request is not None:
        return request.build_absolute_uri(path)

    base_url = (site_url or settings.SITE_URL).rstrip("/") + "/"
    return urljoin(base_url, path.lstrip("/"))


def _send_template_email(subject, template_name, context, recipient):
    html_message = render_to_string(template_name, context)
    send_mail(
        subject=subject,
        message=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        html_message=html_message,
        fail_silently=False,
    )


def send_verification_email(user, *, request=None, site_url=None):
    uid = _uid_for_user(user)
    token = email_verification_token_generator.make_token(user)
    verification_url = _build_absolute_uri(
        "user-email-verify",
        request=request,
        site_url=site_url,
        uidb64=uid,
        token=token,
    )
    _send_template_email(
        "Verify your Nepsenotopi account",
        "user/emails/verification_email.html",
        {"user": user, "verification_url": verification_url},
        user.email,
    )


def send_password_reset_email(user, *, request=None, site_url=None):
    uid = _uid_for_user(user)
    token = default_token_generator.make_token(user)
    reset_url = _build_absolute_uri(
        "user-password-reset-confirm",
        request=request,
        site_url=site_url,
        uidb64=uid,
        token=token,
    )
    _send_template_email(
        "Reset your Nepsenotopi password",
        "user/emails/password_reset_email.html",
        {"user": user, "reset_url": reset_url, "uid": uid, "token": token},
        user.email,
    )
