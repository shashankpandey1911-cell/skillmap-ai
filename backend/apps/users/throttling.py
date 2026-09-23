"""Custom throttle classes for sensitive endpoints."""

from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    """Rate limit login attempts to prevent brute force attacks."""

    scope = "login"


class RegisterThrottle(AnonRateThrottle):
    """Rate limit registration to prevent spam accounts."""

    scope = "register"


class PasswordResetThrottle(AnonRateThrottle):
    """Rate limit password reset requests."""

    scope = "password_reset"


class ResendVerificationThrottle(AnonRateThrottle):
    """Rate limit email-verification requests (verify + resend)."""

    scope = "email_verification"
