from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User


class PhoneAuthBackend(BaseBackend):
    """
    Custom authentication backend that allows users to log in using their phone number
    instead of username.
    """
    
    def authenticate(self, request, phone=None, password=None, **kwargs):
        """
        Authenticate a user based on phone number and password.
        """
        if phone is None or password is None:
            return None
            
        try:
            user = User.objects.get(phone=phone)
            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get a user by their ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

