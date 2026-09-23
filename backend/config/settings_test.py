"""Test-specific settings: inherits everything from settings.py but disables
throttling so the test suite is not affected by rate-limit counters.

View-level throttle_classes (RegisterThrottle, etc.) still resolve their
scope keys against DEFAULT_THROTTLE_RATES, so we keep the rates defined
but set them very high to avoid 429s during tests.
"""

from config.settings import *  # noqa: F401, F403

# Disable default throttle classes; keep rates so explicit view-level
# throttle_classes don't hit a KeyError on scope lookup.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100000/hour",
        "user": "100000/hour",
        "login": "100000/minute",
        "register": "100000/hour",
        "password_reset": "100000/hour",
    },
}

# Use in-memory cache for tests (avoids stale throttle cache across test databases).
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email verification is opt-out in tests: suites register users via the API
# and sign in immediately. The verification flow itself is covered by the
# dedicated tests in apps.users.tests.EmailVerificationTests.
EMAIL_VERIFICATION_REQUIRED = False

# Missing "email_verification" rate would KeyError in ResendVerificationThrottle.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_RATES": {
        **REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],  # noqa: F405
        "email_verification": "100000/hour",
    },
}
