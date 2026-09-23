"""Email-verification services: token issuance, verification, and emails.

Emails are sent through Django's configured backend (console in DEBUG,
SMTP in production). SMTP credentials come exclusively from environment
variables — nothing is hardcoded here.
"""

import hashlib
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.users.models import EmailVerificationToken

logger = logging.getLogger(__name__)

User = get_user_model()

# Outcomes returned to the API layer; all are safe to expose to clients.
VERIFIED = "verified"
ALREADY_VERIFIED = "already_verified"
EXPIRED = "expired"
INVALID = "invalid"

# Shown when an unverified user tries to sign in; the frontend keys its
# "resend verification email" option off this exact wording.
UNVERIFIED_LOGIN_MESSAGE = (
    "Please verify your email address before signing in. "
    "Check your inbox for the verification link."
)


def send_verification_email(user) -> bool:
    """Issue a fresh single-use token and email the link. True when sent."""
    _token_obj, raw_token = EmailVerificationToken.issue(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"{settings.FRONTEND_URL}/auth/verify-email?uid={uid}&token={raw_token}"
    hours = settings.EMAIL_VERIFICATION_TOKEN_HOURS
    try:
        send_mail(
            subject="SkillMap AI — Verify your email address",
            message=(
                f"Hi {user.get_full_name() or user.username},\n\n"
                "Welcome to SkillMap AI! Please confirm your email address "
                "to activate your account.\n\n"
                f"Verify your email: {link}\n\n"
                f"This link is valid for {hours} hours and can be used once.\n"
                "If you did not create this account, you can safely ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        # Registration must not fail because SMTP is unavailable; the user
        # can request a fresh link via /auth/resend-verification.
        logger.exception("Could not send verification email to %s", user.email)
        return False
    return True


def verify_email_token(uidb64: str, token: str) -> tuple[str, object | None]:
    """Validate a verification link. Returns (outcome, user).

    Outcomes: VERIFIED, ALREADY_VERIFIED, EXPIRED, INVALID.
    Tokens are single-use: a reused token is reported as already verified
    (the first use succeeded), never as an error.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return INVALID, None

    if user.is_email_verified:
        return ALREADY_VERIFIED, user

    token_obj = (
        EmailVerificationToken.objects.select_related("user")
        .filter(token=hashlib.sha256(token.encode()).hexdigest())
        .first()
    )
    if token_obj is None or token_obj.user_id != user.pk:
        return INVALID, user
    if token_obj.is_used:
        return ALREADY_VERIFIED, user
    if token_obj.is_expired:
        return EXPIRED, user

    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])
    token_obj.used_at = timezone.now()
    token_obj.save(update_fields=["used_at"])
    # Housekeeping: drop any other outstanding tokens for this user.
    EmailVerificationToken.objects.filter(user=user).exclude(pk=token_obj.pk).delete()
    return VERIFIED, user
