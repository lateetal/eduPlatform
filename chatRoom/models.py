from django.db import models
from homepage.models import Course
from login.models import User

class Discussion(models.Model):
    dno = models.AutoField(primary_key=True)
    cno = models.ForeignKey('homepage.Course', on_delete=models.CASCADE)#所属课程
    ownerNo = models.ForeignKey('login.User', on_delete=models.CASCADE)#所属用户
    dtitle = models.TextField()# 不用指定大小 适合储存长文本
    dinfo = models.TextField()
    postTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)
    havePic = models.BooleanField(default=False)
    like = models.IntegerField(default=0)

class Review(models.Model):
    rno = models.AutoField(primary_key=True)
    dno = models.ForeignKey('Discussion', on_delete=models.CASCADE)
    ownerNo = models.ForeignKey('login.User', on_delete=models.CASCADE)
    rinfo = models.TextField()
    postTime = models.DateTimeField(auto_now_add=True)
    likeNum = models.IntegerField(default=0)
    havePic = models.BooleanField(default=False)
    isTop = models.BooleanField(default=False)

class PictureDisscussion(models.Model):
    dno = models.ForeignKey('Discussion', on_delete=models.CASCADE)
    pfile = models.FileField(upload_to='pictures')

class PictureReview(models.Model):
    rno = models.ForeignKey('Review', on_delete=models.CASCADE)
    pfile = models.FileField(upload_to='pictures')

class Like(models.Model):
    rno = models.ForeignKey('Review', on_delete=models.CASCADE)
    userNo = models.ForeignKey('login.User', on_delete=models.CASCADE)

class DiscussionLike(models.Model):
    dno = models.ForeignKey('Discussion', on_delete=models.CASCADE)
    userNo = models.ForeignKey('login.User', on_delete=models.CASCADE)

#收藏夹 每个用户至少一个默认收藏夹
class FavoritesFolder(models.Model):
    fno = models.AutoField(primary_key=True)
    userNo = models.ForeignKey('login.User', on_delete=models.CASCADE)
    fname = models.CharField(max_length=50)
    fstatus = models.BooleanField(default=False)#他人是否可见

#收藏夹中的收藏信息
class Favorite(models.Model):
    fno = models.ForeignKey('FavoritesFolder', on_delete=models.CASCADE)
    dno = models.ForeignKey('Discussion', on_delete=models.CASCADE)

#@他人的信息
class atMessage(models.Model):
    rno = models.ForeignKey('Review', on_delete=models.CASCADE)#属于哪条回复
    senderno = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiverno = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    sendTime = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)


