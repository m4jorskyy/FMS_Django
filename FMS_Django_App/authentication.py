from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from .models import User


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Tylko cookies - brak wsparcia dla Authorization header
        token = request.COOKIES.get('access_token')

        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('id')

            if not user_id:
                raise AuthenticationFailed('Invalid token')

            user = User.objects.get(id=user_id)

            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')