from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
import uuid
import secrets


class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    CUSTOMER = 'CUSTOMER', 'Customer'


class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    def __str__(self):
        return self.email


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    class Meta:
        db_table = 'admins'

    def __str__(self):
        return f"Admin: {self.user.email}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return f"Customer: {self.user.email}"


class PendingUser(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    verification_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    token_expiration_hours = models.IntegerField(default=24)

    class Meta:
        db_table = 'pending_users'

    def is_token_expired(self):
        """Check if verification token has expired"""
        expiration_time = self.created_at + timedelta(hours=self.token_expiration_hours)
        return timezone.now() > expiration_time

    def renew_token(self):
        """Generate new verification token"""
        self.verification_token = str(uuid.uuid4())
        self.created_at = timezone.now()
        self.save()

    def __str__(self):
        return self.email


class TokenType(models.TextChoices):
    ACCESS = 'ACCESS', 'Access Token'
    REFRESH = 'REFRESH', 'Refresh Token'
    VERIFICATION = 'VERIFICATION', 'Verification Token'


class Token(models.Model):
    value = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token_type = models.CharField(max_length=20, choices=TokenType.choices)

    class Meta:
        db_table = 'tokens'

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at

    def refresh(self, new_expires_at):
        """Refresh token with new value and expiration"""
        self.value = str(uuid.uuid4())
        self.created_at = timezone.now()
        self.expires_at = new_expires_at
        self.save()

    def __str__(self):
        return f"{self.token_type}: {self.value[:20]}..."


class Code(models.Model):
    value = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_minutes = models.IntegerField(default=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='codes')

    class Meta:
        db_table = 'codes'

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = self.generate_six_digit_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_six_digit_code():
        """Generate a secure 6-digit code"""
        return str(secrets.randbelow(900000) + 100000)

    def is_expired(self):
        """Check if code has expired"""
        expiration_time = self.created_at + timedelta(minutes=self.expiration_minutes)
        return timezone.now() > expiration_time

    def __str__(self):
        return f"Code for {self.user.email}: {self.value}"


class Session(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='session')
    access_token = models.OneToOneField(
        Token, 
        on_delete=models.CASCADE, 
        related_name='access_session'
    )
    refresh_token = models.OneToOneField(
        Token, 
        on_delete=models.CASCADE, 
        related_name='refresh_session'
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sessions'

    def __str__(self):
        return f"Session for {self.user.email}"