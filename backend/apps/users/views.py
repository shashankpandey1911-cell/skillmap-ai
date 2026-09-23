"""Authentication views.

Password hashing: Django's default PBKDF2 via user.set_password().
JWT: access + refresh tokens (SimpleJWT); logout blacklists the refresh
token server-side.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView

from apps.users.throttling import (
    LoginThrottle,
    RegisterThrottle,
    PasswordResetThrottle,
    ResendVerificationThrottle,
)
from apps.users.services import (
    ALREADY_VERIFIED,
    EXPIRED,
    INVALID,
    UNVERIFIED_LOGIN_MESSAGE,
    VERIFIED,
    send_verification_email,
    verify_email_token,
)

from apps.users.serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        detail = "Check your email to verify your account."
        if settings.EMAIL_VERIFICATION_REQUIRED:
            # Console backend in DEBUG; never blocks registration — the user
            # can request a fresh link via /auth/resend-verification.
            send_verification_email(user)
            # No tokens until the email is confirmed: login is the gate.
            return Response({"user": UserSerializer(user).data, "detail": detail},
                            status=status.HTTP_201_CREATED)

        # Verification disabled (tests / local demos): keep the legacy
        # auto-login response shape used by the API suites.
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
                "detail": detail,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    """POST /auth/verify-email — consumes the emailed verification link."""

    permission_classes = [AllowAny]
    throttle_classes = [ResendVerificationThrottle]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        outcome, _user = verify_email_token(
            serializer.validated_data["uidb64"], serializer.validated_data["token"]
        )
        messages = {
            VERIFIED: "Your email has been verified. You can now sign in.",
            ALREADY_VERIFIED: "This email address has already been verified. You can sign in.",
            EXPIRED: "This verification link has expired. Please request a new one.",
            INVALID: "This verification link is invalid.",
        }
        res = Response({"detail": messages[outcome], "status": outcome})
        res.status_code = (
            status.HTTP_200_OK if outcome in (VERIFIED, ALREADY_VERIFIED) else status.HTTP_400_BAD_REQUEST
        )
        return res


class ResendVerificationView(APIView):
    """POST /auth/resend-verification — emails a fresh link.

    Accepts either an email address (public form) or an authenticated user
    (banner retry). Always returns the same response to prevent enumeration.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ResendVerificationThrottle]

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()

        user = User.objects.filter(email__iexact=email).first()
        if user and user.is_active and not user.is_email_verified:
            send_verification_email(user)
        return Response(
            {"detail": "If an unverified account exists for that email, a new verification link has been sent."},
            status=status.HTTP_200_OK,
        )


class LogoutView(TokenBlacklistView):
    """POST /auth/logout with {'refresh': ...} — blacklists the token.

    Returns 200 on success; a subsequent refresh with the same token fails.
    """


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()

        # Always return the same response to avoid account enumeration.
        user = User.objects.filter(email__iexact=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            send_mail(
                subject="SkillMap AI — Reset your password",
                message=(
                    f"Hi {user.get_full_name() or user.username},\n\n"
                    "We received a request to reset your SkillMap AI password.\n"
                    f"Open this link to choose a new password:\n\n{link}\n\n"
                    "If you did not request this, you can safely ignore this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        return Response(
            {
                "detail": (
                    "If an account exists for that email, a password reset "
                    "link has been sent."
                )
            }
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uidb64"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "The reset link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = serializer.validated_data["token"]
        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "The reset link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["password"])
        # Completing a password reset proves control of the mailbox, so
        # clear any pending verification at the same time.
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=["password", "is_email_verified"])
        else:
            user.save(update_fields=["password"])
        return Response({"detail": "Your password has been reset. You can now log in."})
