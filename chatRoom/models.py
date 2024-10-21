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

class Review(models.Model):
    rno = models.IntegerField(primary_key=True)
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

