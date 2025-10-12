from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import uuid
from ...models import (
    User, Admin, Customer, PendingUser, Token, Code, Session,
    TokenType, UserRole
)


class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def send_email(to_email, subject, body):
        """Send email to user"""
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )


class EmailTemplateService:
    """Service for generating email templates"""
    
    @staticmethod
    def create_account_verification_email(first_name, last_name, token):
        """Create account verification email body"""
        base_url = settings.BASE_URL
        verification_link = f"{base_url}/rr/verify-account?token={token}"
        
        return f"""Hello {first_name} {last_name},

We received a request to register an account using this email address.

If you made this request, please verify your registration by clicking the link below:
{verification_link}

If you did not request this registration, you can safely ignore this email. No account will be created.

Thank you,
CIC Team"""

    @staticmethod
    def create_password_reset_email(first_name, last_name, code):
        """Create password reset email body"""
        return f"""Hello {first_name} {last_name},

We received a request to reset your account password.

To continue, please use the verification code below:

Verification Code: {code}

This code will expire in 5 minutes. 
If you did not request a password reset, you can safely ignore this email. 
Your account will remain secure.

Thank you,
The CIC Team"""


class RegistrationService:
    """Service for handling user registration"""
    
    @staticmethod
    def initiate_registration(first_name, last_name, email, password, role):
        """Start registration process by creating pending user"""
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise ValueError("You're already registered. Try logging in instead.")
        
        # Handle existing pending user
        existing_pending = PendingUser.objects.filter(email=email).first()
        if existing_pending:
            if not existing_pending.is_token_expired():
                raise ValueError("This email has been registered as pending. Awaiting verification.")
            
            # Renew token for expired pending user
            existing_pending.renew_token()
            RegistrationService._send_verification_email(existing_pending, first_name, last_name)
            return "Verification email resent. Please check your inbox."
        
        # Create new pending user
        pending_user = PendingUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
            role=role,
            verification_token=str(uuid.uuid4())
        )
        
        RegistrationService._send_verification_email(pending_user, first_name, last_name)
        return "Verification email sent. Please check your inbox."
    
    @staticmethod
    def _send_verification_email(pending_user, first_name, last_name):
        """Send verification email to pending user"""
        email_body = EmailTemplateService.create_account_verification_email(
            first_name, last_name, pending_user.verification_token
        )
        EmailService.send_email(pending_user.email, "Verify Account", email_body)
    
    @staticmethod
    def check_verification_status(token):
        """Check the status of a verification token"""
        pending_user = PendingUser.objects.filter(verification_token=token).first()
        
        if not pending_user:
            return {
                'state': 'Verified',
                'email': None,
                'name': None
            }
        
        return {
            'state': 'Expired' if pending_user.is_token_expired() else 'Pending',
            'email': pending_user.email,
            'name': f"{pending_user.first_name} {pending_user.last_name}"
        }
    
    @staticmethod
    def complete_registration(email):
        """Complete registration by converting pending user to active user"""
        pending_user = PendingUser.objects.filter(email=email).first()
        
        if not pending_user:
            raise ValueError("Pending user not found")
        
        # Create user
        user = User.objects.create(
            first_name=pending_user.first_name,
            last_name=pending_user.last_name,
            email=pending_user.email,
            password=pending_user.password,
            role=pending_user.role
        )
        
        # Create role-specific profile
        if user.role == UserRole.CUSTOMER:
            Customer.objects.create(user=user)
        else:
            Admin.objects.create(user=user)
        
        # Delete pending user
        pending_user.delete()
        
        return f"Account: {user.email} has been registered"


class SessionService:
    """Service for managing user sessions"""
    
    @staticmethod
    def update_or_create_session(user):
        """Create or update user session"""
        try:
            session = Session.objects.get(user=user)
            
            # Refresh tokens
            session.access_token.refresh(timezone.now() + timedelta(hours=1))
            session.refresh_token.refresh(timezone.now() + timedelta(days=30))
            session.active = True
            session.save()
            
            return session
        except Session.DoesNotExist:
            # Create new tokens
            access_token = Token.objects.create(
                user=user,
                token_type=TokenType.ACCESS,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            
            refresh_token = Token.objects.create(
                user=user,
                token_type=TokenType.REFRESH,
                expires_at=timezone.now() + timedelta(days=30)
            )
            
            # Create session
            session = Session.objects.create(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                active=True
            )
            
            return session
    
    @staticmethod
    def refresh_token(refresh_token_value):
        """Refresh access token using refresh token"""
        try:
            session = Session.objects.get(refresh_token__value=refresh_token_value)
        except Session.DoesNotExist:
            raise ValueError("Invalid refresh token")
        
        if session.refresh_token.is_expired():
            raise ValueError("Refresh token has expired")
        
        # Refresh access token
        session.access_token.refresh(timezone.now() + timedelta(hours=1))
        
        return session
    
    @staticmethod
    def validate_access_token(token_value):
        """Validate access token and return session"""
        try:
            session = Session.objects.select_related('user', 'access_token').get(
                access_token__value=token_value
            )
        except Session.DoesNotExist:
            raise ValueError("Invalid access token")
        
        if session.access_token.is_expired():
            raise ValueError("Access token has expired")
        
        return session


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def login(email, password):
        """Authenticate user and create session"""
        # Check if user is pending
        if PendingUser.objects.filter(email=email).exists():
            raise ValueError("Please verify your account to continue.")
        
        # Get user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("User not found")
        
        # Verify password
        if not user.check_password(password):
            raise ValueError("Incorrect Password")
        
        # Create/update session
        session = SessionService.update_or_create_session(user)
        
        # Update last login
        user.update_last_login()
        
        return {
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            },
            'session': {
                'id': session.id,
                'accessToken': session.access_token.value,
                'refreshToken': session.refresh_token.value,
                'expiresAt': session.access_token.expires_at.isoformat()
            }
        }
    
    @staticmethod
    def validate_session(auth_header):
        """Validate session from authorization header"""
        if not auth_header or not auth_header.startswith('Bearer '):
            raise ValueError("Missing authorization header")
        
        token = auth_header[7:]
        session = SessionService.validate_access_token(token)
        
        if not session.active:
            raise ValueError("Session is inactive")
        
        return {"message": "Session is validated"}


class PasswordResetService:
    """Service for password reset operations"""
    
    @staticmethod
    def initiate_password_reset(email):
        """Start password reset process"""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("User not found")
        
        # Delete all existing codes for this user
        Code.objects.filter(user=user).delete()
        
        # Create new code
        code = Code.objects.create(
            user=user,
            expiration_minutes=5
        )
        
        # Send email
        email_body = EmailTemplateService.create_password_reset_email(
            user.first_name, user.last_name, code.value
        )
        EmailService.send_email(email, "Verify Password Reset", email_body)
    
    @staticmethod
    def verify_reset_code(code_value):
        """Verify reset code and return reset token"""
        try:
            code = Code.objects.select_related('user').get(value=code_value)
        except Code.DoesNotExist:
            raise ValueError("Verification code not found or has expired.")
        
        if code.is_expired():
            code.delete()
            raise ValueError("Verification code expired.")
        
        # Create verification token
        token = Token.objects.create(
            user=code.user,
            token_type=TokenType.VERIFICATION,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        
        # Delete used code
        code.delete()
        
        return token.value
    
    @staticmethod
    def reset_password(token_value, new_password):
        """Reset user password using token"""
        try:
            token = Token.objects.select_related('user').get(value=token_value)
        except Token.DoesNotExist:
            raise ValueError("Token not found")
        
        if token.is_expired():
            token.delete()
            raise ValueError("Token expired")
        
        user = token.user
        
        # Check if new password is same as current
        if user.check_password(new_password):
            raise ValueError("Your new password cannot be the same as your current password.")
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Delete used token
        token.delete()


# Import make_password here to avoid circular import
from django.contrib.auth.hashers import make_password