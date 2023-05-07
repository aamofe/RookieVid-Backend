from django.db import models

# Create your models here.
class Video(models.Model):
    label=models.CharField("标签",default="娱乐",max_length=255)
    title=models.CharField('视频标题',max_length=255)
    description=models.CharField('视频描述',max_length=255)
    video_path = models.CharField('视频地址',null=True,max_length=255)
    cover_path=models.CharField('封面地址',null=True,max_length=255)
    # video_file = models.FileField(upload_to='video_file/',null=True)
    # video_cover=models.FileField(upload_to='video_cover',null=True)
    
    # thumbnail_url=models.CharField('视频略缩图地址',max_length=255)
    user_id=models.IntegerField('视频创建者ID' )
    created_at=models.DateTimeField('创建时间',auto_now_add=True)
    reviewed_at=models.DateTimeField('审核时间',null=True)
    reviewed_status=models.IntegerField('审核状态',default=0)
    reviewed_result=models.IntegerField('审核结果',default=0)
    reviewed_reason=models.CharField('审核原因',max_length=255)
    play_amount=models.IntegerField('播放量',default=0)
    hotness=models.IntegerField('热度',default=0)
    like=models.IntegerField('点赞数',default=0)
    class Meta:
        app_label = 'videos'

class Like(models.Model):
    user_id=models.IntegerField('点赞者ID' )
    video_id=models.IntegerField('被点赞的视频ID' )
    created_at=models.DateTimeField('点赞时间', auto_now_add=True)
    class Meta:
        app_label = 'videos'

class Comment(models.Model):
    user_id = models.IntegerField('评论者ID' )
    video_id = models.IntegerField('被评论的视频ID' )
    content=models.CharField('评论内容',max_length=255)
    created_at = models.DateTimeField('评论时间',auto_now_add=True)
    class Meta:
        app_label = 'videos'

class Reply(models.Model):
    #id = models.IntegerField('回复ID',primary_key=True )
    user_id = models.IntegerField('回复者ID' )
    comment_id = models.IntegerField('所属评论ID' )
    content=models.CharField('回复内容',max_length=255)
    created_at = models.DateTimeField('回复时间', auto_now_add=True)
    class Meta:
        app_label = 'videos'

class Collect(models.Model):
    user_id = models.IntegerField('收藏者ID'  )
    video_id = models.IntegerField('被收藏的视频ID'  )
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)