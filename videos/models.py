import os.path
from time import timezone

from django.db import models

from RookieVid_Backend.settings import VIDEO_URL, COVER_URL
from accounts.models import User


# Create your models here.
class Video(models.Model):
    label=models.CharField(verbose_name='标签',default="娱乐",max_length=255)
    title=models.CharField(verbose_name='视频标题',max_length=255)
    description=models.CharField(verbose_name='视频描述',max_length=255)
    video_file=models.FileField(verbose_name='视频',upload_to='video_file/')
    cover_file=models.FileField(verbose_name='图片',upload_to='cover_file/')

    user = models.ForeignKey(User, verbose_name='所属用户',null=True, on_delete=models.CASCADE)
    created_at=models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    reviewed_at=models.DateTimeField(verbose_name='审核时间',null=True)
    reviewed_status=models.IntegerField(verbose_name='审核状态',default=0) #0未审核 1审核通过 2需复核

    view_amount=models.IntegerField(verbose_name='播放量',default=0)
    fav_amount=models.IntegerField(verbose_name='收藏量',default=0)
    like_amount=models.IntegerField(verbose_name='点赞数',default=0)
    class Meta:
        app_label = 'videos'
        #db_table = "video"  # 数据库表名
    # def save(self,*args,**kwargs):
    #     super().save(*args,**kwargs)
    #     if not self.video_file:
    #         return
    #     video_id=self.pk
    #     video_name=os.path.join(VIDEO_URL,f'{video_id}.mp4')
    #     cover_name = os.path.join(COVER_URL, f'{video_id}.png')
    #     self.video_file.name=video_name
    #     self.cover_file.name=cover_name
    #     #super().save(*args,**kwargs)
    def to_dict(self):
        return {
            'id':self.id,
            'label':self.label,
            'video':self.video_file,

        }

class Like(models.Model):
    user = models.ForeignKey(User, verbose_name='所属用户', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, verbose_name='视频所属用户', on_delete=models.CASCADE)
    created_at=models.DateTimeField(verbose_name='点赞时间', auto_now_add=True)
    class Meta:
        app_label = 'videos'

class Comment(models.Model):
    user_id = models.IntegerField(verbose_name='评论者ID' )
    video_id = models.IntegerField(verbose_name='被评论的视频ID' )
    content=models.CharField(verbose_name='评论内容',max_length=255)
    created_at = models.DateTimeField(verbose_name='评论时间',auto_now_add=True)
    class Meta:
        app_label = 'videos'

class Reply(models.Model):
    #id = models.IntegerField(verbose_name='回复ID',primary_key=True )
    user_id = models.IntegerField(verbose_name='回复者ID' )
    comment_id = models.IntegerField(verbose_name='所属评论ID' )
    content=models.CharField(verbose_name='回复内容',max_length=255)
    created_at = models.DateTimeField(verbose_name='回复时间', auto_now_add=True)
    class Meta:
        app_label = 'videos'

class Favorite(models.Model):
    title = models.CharField(verbose_name='默认收藏夹', max_length=64)
    description = models.TextField(verbose_name='描述')
    status = models.IntegerField(verbose_name="是否为私有", default=0)  # 0 - 公开    1 - 私有
    user_id=models.IntegerField(verbose_name='所属用户')
    avatar_url = models.CharField(verbose_name='封面路径', max_length=128)

class Favlist(models.Model):
    favorite_id = models.IntegerField(verbose_name='收藏夹编号', default=0)
    video_id = models.IntegerField(verbose_name='视频编号', default=0)
