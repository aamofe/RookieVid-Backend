from django.db import models
from datetime import timedelta, timezone
import pytz

shanghai_tz = pytz.timezone('Asia/Shanghai')

# Create your models here.

class Notification(models.Model):
    send_to = models.IntegerField('通知对象ID')
    send_from = models.IntegerField('通知者ID', default=0)  # 如果是管理员填0，其他用户正常填user.id
    title = models.CharField('通知标题', max_length=64)
    content = models.CharField('通知内容', max_length=255)
    # 管理员自定义的是0，对用户的是1（关注），对视频的是2（点赞、收藏、评论、审核），对评论的是3（回复），对投诉的是4（处理投诉）
    link_type = models.IntegerField('通知类型', default=0)
    link_id = models.IntegerField('关联视频/评论ID', default=0)  # 如果type是0，link_id=0；如果type非0，是对应id
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('通知创建时间', auto_now_add=True)

    def to_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return {
            'id': self.id,
            'send_to': self.send_to,
            'send_from': self.send_from,
            'title': self.title,
            'content': self.content,
            'link_type': self.link_type,
            'link_id': self.link_id,
            'is_read': self.is_read,
            'create_at': created_at_shanghai,
        }

    def to_simple_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'create_at': created_at_shanghai,
        }

