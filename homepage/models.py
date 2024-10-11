from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Student(models.Model):
    sno = models.CharField(max_length = 8,primary_key = True)
    sname = models.CharField(max_length = 20)
    smail = models.CharField(max_length = 30)
    sconcern = models.IntegerField(validators=[MaxValueValidator(500)]) #关注人数
    sfans = models.IntegerField(validators=[MaxValueValidator(500)]) #粉丝人数
    sfavor = models.IntegerField(validators=[MaxValueValidator(500)]) #关注帖子

class Teacher(models.Model):
    tno = models.CharField(max_length = 8,primary_key = True)
    tname = models.CharField(max_length = 20)
    tmail = models.CharField(max_length = 30)
    toffice = models.CharField(max_length = 10)
    tphone = models.CharField(max_length = 15)
    tintro = models.CharField(max_length = 500)

class Course(models.Model):
    cno = models.CharField(max_length = 8,primary_key = True)#唯一课号
    course_no = models.CharField(max_length = 8)#课程号
    course_class = models.CharField(max_length = 2)#班级号
    cname = models.CharField(max_length = 20)
    cintro = models.CharField(max_length = 500) #介绍
    coutline = models.CharField(max_length = 100) #大纲
    calender = models.CharField(max_length = 100) #教学日历
    tno = models.ForeignKey('Teacher', on_delete = models.CASCADE)
    picAddr = models.CharField(max_length = 100, default="NULL") #课程图片 默认为空

class ChooseClass(models.Model):
    sno = models.ForeignKey('Student', on_delete = models.CASCADE)
    cno = models.ForeignKey('Course', on_delete = models.CASCADE)
    ccgrade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)]) #设置min和max值



