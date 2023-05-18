from django.db import models

# Create your models here.
class Comlpaint(models.Model):
    user_id = models.IntegerField('投诉者ID')
    video_id = models.IntegerField('被投诉的视频ID')
    reason=models.CharField('投诉原因',max_length=255)
    status=models.IntegerField('处理状态')
    created_at = models.DateTimeField('投诉时间', auto_now_add=True)