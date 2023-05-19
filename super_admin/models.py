from django.db import models

# Create your models here.
class Complain(models.Model):
    user_id = models.IntegerField('投诉者ID')
    video_id = models.IntegerField('被投诉的视频ID')
    reason=models.CharField('投诉原因',max_length=255)
    status=models.IntegerField('处理状态')
    created_at = models.DateTimeField('投诉时间', auto_now_add=True)
    is_message_sent=models.IntegerField('是否已经给投诉人发送消息',default=0)

    def to_dict(self):
        return {
            'id':self.id,
            'user_id':self.user_id,
            'video_id':self.user_id,
            'reason':self.reason,
            'status':self.status,
            'created_at':self.created_at,
            'is_message_sent':self.is_message_sent
        }