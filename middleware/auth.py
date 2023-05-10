from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from jose import jwt, ExpiredSignatureError, JWTError

from accounts.models import User


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.META.get('HTTP_Authorization'.upper())
        if token:
            token = token.replace('Bearer ', '')
            try:
                jwt_token = jwt.decode(token, settings.SECRET_KEY)
            except ExpiredSignatureError:
                return False
            except JWTError:
                return False

            user = User.objects.get(uid=jwt_token.get('uid'))
            request.user = user

        return
