from django.db import models

# Create your models here.
class Comlpaint(models.Model):
    id = models.IntegerField('投诉ID', max_length=10)
    user_id = models.IntegerField('投诉者ID', max_length=10)
    video_id = models.IntegerField('被投诉的视频ID', max_length=10)
    reason=models.CharField('投诉原因',max_length=255)
    status=models.IntegerField('处理状态')
    created_at = models.DateTimeField('点赞时间')