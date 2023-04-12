from django.db import models

# Create your models here.
class User(models.Model):
    id=models.IntegerField('用户ID',max_length=10)#我的想法是，像qq账号一样，10位，完全不重复
    username=models.CharField('用户名',max_length=20)
    email=models.CharField('邮箱')
    password=models.CharField('密码',max_length=16)
    avatar_url=models.CharField('头像地址')
    created_at=models.DateTimeField('创建时间')
    status=models.IntegerField('状态')

class Category(models.Model):
    id=models.IntegerField('分类ID',max_length=10)#从1开始取吧
    name=models.CharField('分类名称',max_length=20)
class Video(models.Model):
    id=models.IntegerField('视频ID',max_length=10)
    title=models.CharField('视频标题',max_length=20)
    description=models.CharField('视频描述',max_length=255)
    url=models.CharField('视频地址',max_length=255)
    thumbnail_url=models.CharField('视频略缩图地址',max_length=255)
    category_id=models.IntegerField('视频所属分类ID',max_length=10)
    user_id=models.IntegerField('视频创建者ID',max_length=10)
    created_at=models.DateTimeField('创建时间',)
    reviewed_at=models.DateTimeField('审核时间')
    reviewed_status=models.IntegerField('审核状态')
    reviewed_result=models.IntegerField('审核结果')
    reviewed_reason=models.CharField('审核原因')
    play_amount=models.IntegerField('播放量')


