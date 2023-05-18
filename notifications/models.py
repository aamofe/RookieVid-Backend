from django.db import models

# Create your models here.

class Notification(models.Model):
    send_to = models.CharField('通知对象ID', max_length=10)
    send_from = models.CharField('通知者', max_length=10)
    content = models.CharField('通知内容', max_length=255)
    # link=models.CharField('跳转链接',max_length=255)
    created_at = models.DateTimeField('通知创建时间', auto_now_add=True)