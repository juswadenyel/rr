from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import json
from .services import (
    RegistrationService, AuthService, PasswordResetService, SessionService
)
from ...models import Session, UserRole, Admin
from functools import wraps


# Decorators for authentication
def require_auth(view_func):
    """Decorator to require authentication"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'message': 'Missing or invalid authorization header'},
                status=401
            )
        
        token = auth_header[7:]
        
        try:
            session = SessionService.validate_access_token(token)
            
            if not session.active:
                return JsonResponse(
                    {'message': 'Session is inactive'},
                    status=401
                )
            
            request.current_user = session.user
            request.current_session = session
            
            return view_func(request, *args, **kwargs)
        except ValueError as e:
            return JsonResponse({'message': str(e)}, status=401)
    
    return wrapper


def require_admin_auth(view_func):
    """Decorator to require admin authentication"""
    @wraps(view_func)
    @require_auth
    def wrapper(request, *args, **kwargs):
        if request.current_user.role != UserRole.ADMIN:
            return JsonResponse(
                {'message': 'Admin privileges required'},
                status=403
            )
        
        try:
            request.current_admin = Admin.objects.get(user=request.current_user)
        except Admin.DoesNotExist:
            return JsonResponse(
                {'message': 'Admin profile not found'},
                status=403
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# API Views
@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    """Handle user registration"""
    try:
        data = json.loads(request.body)
        message = RegistrationService.initiate_registration(
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            email=data.get('email'),
            password=data.get('password'),
            role=data.get('role')
        )
        return JsonResponse({'success': True, 'message': message}, status=200)
    except ValueError as e:
        status = 409 if 'pending' in str(e).lower() else 400
        return JsonResponse({'success': False, 'message': str(e)}, status=status)


@csrf_exempt
@require_http_methods(["POST"])
def verify_status(request):
    """Check verification status of a token"""
    try:
        data = json.loads(request.body)
        response = RegistrationService.check_verification_status(data.get('token'))
        
        message_map = {
            'Pending': 'Awaiting verification',
            'Expired': 'Token has expired',
            'Verified': 'Token not found or already used'
        }
        
        # Always return success: true, let the frontend handle state
        return JsonResponse(
            {
                'success': True,
                'message': message_map[response['state']],
                'data': response
            },
            status=200
        )
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def verify_account(request):
    """Complete account verification"""
    try:
        data = json.loads(request.body)
        message = RegistrationService.complete_registration(data.get('email'))
        return JsonResponse({'success':True, 'message': message}, status=200)
    except ValueError as e:
        return JsonResponse({'success':False, 'message': str(e)}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def signin(request):
    """Handle user login"""
    try:
        data = json.loads(request.body)
        response = AuthService.login(data.get('email'), data.get('password'))
        return JsonResponse({
            'success':True,
            'message': 'Login successful',
            'data': response
        }, status=200)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def send_code_to_mail(request):
    """Send password reset code to email"""
    try:
        data = json.loads(request.body)
        PasswordResetService.initiate_password_reset(data.get('email'))
        return JsonResponse({
            'success': True,
            'message': 'Verification code sent! Please check your inbox.'
        }, status=200)
    except ValueError as e:
        return JsonResponse({'success':False, 'message': str(e)}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def verify_code(request):
    """Verify password reset code"""
    try:
        data = json.loads(request.body)
        reset_token = PasswordResetService.verify_reset_code(data.get('code'))
        return JsonResponse({
            'success':True,
            'message': 'Code verified! You can now reset your password.',
            'data': reset_token
        }, status=200)
    except ValueError as e:
        return JsonResponse({'success':False, 'message': str(e)}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def reset_password(request):
    """Reset user password"""
    try:
        data = json.loads(request.body)
        PasswordResetService.reset_password(data.get('token'), data.get('password'))
        return JsonResponse({
            'success':True,
            'message': 'Password reset successful! You can now login'
        }, status=200)
    except ValueError as e:
        return JsonResponse({'success':False, 'message': str(e)}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    """Refresh access token"""
    try:
        data = json.loads(request.body)
        session = SessionService.refresh_token(data.get('token'))
        return JsonResponse({
            'success':True,
            'message': 'Token refreshed',
            'data': {
                'accessToken': session.access_token.value,
                'refreshToken': session.refresh_token.value,
                'expiresAt': session.access_token.expires_at.isoformat()
            }
        }, status=200)
    except ValueError as e:
        return JsonResponse({'success':False,'message': str(e)}, status=404)


@require_http_methods(["GET"])
def validate_session(request):
    """Validate current session"""
    try:
        auth_header = request.headers.get('Authorization')
        response = AuthService.validate_session(auth_header)
        return JsonResponse(response, status=200)
    except ValueError as e:
        return JsonResponse({'message': str(e)}, status=404)


@require_auth
@require_http_methods(["GET"])
def get_current_user(request):
    """Get current authenticated user"""
    user = request.current_user
    return JsonResponse({
        'message': 'User retrieved successfully',
        'data': {
            'id': user.id,
            'email': user.email,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'role': user.role
        }
    }, status=200)


@require_auth
@require_http_methods(["GET"])
def signout(request):
    """Sign out user"""
    session = request.current_session
    session.active = False
    session.save()
    return JsonResponse({'success':True, 'message': 'Signed out successfully'}, status=200)


# Page Views (if using Django templates)
def signin_page(request):
    """Render sign-in page"""
    return render(request, 'rr_app/auth/sign-in.html')


def signup_page(request):
    """Render sign-up page"""
    return render(request, 'rr_app/auth/sign-up.html')


def forgot_password_page(request):
    """Render forgot password page"""
    return render(request, 'rr_app/auth/fpass.html')


def reset_password_page(request):
    """Render reset password page"""
    return render(request, 'rr_app/auth/reset_pass.html')


def verify_account_page(request):
    """Render verify account page"""
    return render(request, 'rr_app/auth/verify_account.html')