import re
from ..models import User
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def validate_password(password):
    min_length = 8
    max_length = 20
    if not password:
        return False, "Password cannot be empty"
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    if len(password) > max_length:
        return False, f"Password cannot exceed {max_length} characters"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def validate_email(email):
    if not email:
        return False, "Email cannot be empty"

    # Simple but practical regex (RFC-compliant is overkill)
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(email_regex, email):
        return False, "Invalid email format"

    return True, "Email is valid"

def create_django_user(user_id, email, first_name, last_name):
    existing_user = User.objects.filter(email=email).first()
    if existing_user:
        return existing_user
    
    django_user = User.objects.create(
        supabase_id=user_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )
    django_user.update_last_login()
    return django_user
