from django.db import models

# Create your models here.
class User(models.Model):
    uid=models.CharField('用户ID', max_length=10)#我的想法是，像qq账号一样，10位，完全不重复
    username=models.CharField('用户名', max_length=20)
    email=models.CharField('邮箱', max_length=20)
    password=models.CharField('密码', max_length=16)
    avatar_url=models.CharField('头像地址', max_length=255)
    created_at=models.DateTimeField('创建时间', auto_now_add=True)
    status=models.IntegerField('状态',default=0)



class Follow(models.Model):
    follower_id = models.IntegerField('粉丝ID'  )
    following_id = models.IntegerField('被关注者ID'  )
    created_at = models.DateTimeField('关注时间', auto_now_add=True)


