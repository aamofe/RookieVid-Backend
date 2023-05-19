from django.db import models


# Create your models here.

class Notification(models.Model):
    send_to = models.IntegerField('通知对象ID')
    send_from = models.CharField('通知者', max_length=20)
    content = models.CharField('通知内容', max_length=255)
    # link=models.CharField('跳转链接',max_length=255)
    created_at = models.DateTimeField('通知创建时间', auto_now_add=True)

    def to_dict(self):
        return {
            'send_to': self.send_to,
            'send_from': self.send_from,
            'content': self.content,
            'create_at': self.created_at,
        }
