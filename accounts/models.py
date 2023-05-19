import datetime

from django.db import models


# Create your models here.
class User(models.Model):
    uid = models.CharField('用户ID', max_length=10)  # 我的想法是，像qq账号一样，10位，完全不重复
    username = models.CharField('用户名', max_length=20)
    email = models.CharField('邮箱', max_length=20)
    password = models.CharField('密码', max_length=16)
    avatar_url = models.CharField('头像地址', max_length=255)
    signature = models.CharField('个性签名', max_length=100)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    status = models.IntegerField('状态', default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'uid': self.uid,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'signature': self.signature
        }


class Follow(models.Model):
    follower_id = models.CharField('粉丝ID', max_length=10)  # 因为用户ID有10位，用integer可能超范围，也可以改成biginteger
    following_id = models.CharField('被关注者ID', max_length=10)
    created_at = models.DateTimeField('关注时间', auto_now_add=True)


class Vcode(models.Model):
    vcode = models.CharField('验证码', max_length=6)
    to_email = models.CharField('邮箱', max_length=20)
    # code_time = models.DateTimeField('发送时间', auto_now_add=True)
    send_at = models.DateTimeField('发送时间', auto_now_add=True)
