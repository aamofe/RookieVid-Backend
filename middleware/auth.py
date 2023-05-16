from django.conf import settings
from django.http import JsonResponse
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
                return JsonResponse({'msg': "登录已过期，请重新登录"})
            except JWTError:
                return JsonResponse({'msg': "用户未登录，请先登录"})
            try:
                user = User.objects.get(uid=jwt_token.get('uid'))
            except User.DoesNotExist:
                return JsonResponse({'msg': "用户不存在，请先注册"})
            request.user = user

        return
