from django.db import models

# Create your models here.

class Notification(models.Model):
    id = models.IntegerField('通知ID', max_length=10)
    user_id = models.IntegerField('通知对象ID', max_length=10)
    content = models.CharField('通知内容', max_length=255)
    link=models.CharField('跳转链接')
    created_at = models.DateTimeField('通知创建时间')