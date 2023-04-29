from django.db import models

# Create your models here.
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

class Like(models.Model):
    id = models.IntegerField('点赞ID', max_length=10)
    user_id=models.IntegerField('点赞者ID', max_length=10)
    video_id=models.IntegerField('被点赞的视频ID', max_length=10)
    created_at=models.DateTimeField('点赞时间')

class Comment(models.Model):
    id = models.IntegerField('评论ID', max_length=10)
    user_id = models.IntegerField('评论者ID', max_length=10)
    video_id = models.IntegerField('被评论的视频ID', max_length=10)
    content=models.CharField('评论内容',max_length=255)
    created_at = models.DateTimeField('点赞时间')

class Reply(models.Model):
    id = models.IntegerField('回复ID', max_length=10)
    user_id = models.IntegerField('回复者ID', max_length=10)
    comment_id = models.IntegerField('所属评论ID', max_length=10)
    content=models.CharField('回复内容',max_length=255)
    created_at = models.DateTimeField('回复时间')