from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError
)

from .jwt_utils import decode_token


User = get_user_model()


class JWTAuth(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('No token provided')
        token = auth_header.split(' ')[1]
        try:
            payload = decode_token(token)
        except ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        request.user = User.objects.get(username=payload.get('username'))
        return True