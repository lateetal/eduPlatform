from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Student(models.Model):
    sno = models.CharField(max_length = 20,primary_key = True)
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

#教师发给选课学生的通知
class CourseMessage(models.Model):
    mno = models.AutoField(primary_key = True)#通知编号
    mcourse = models.ForeignKey('Course', on_delete = models.CASCADE)#来源课程
    msend = models.ForeignKey('Teacher', on_delete = models.CASCADE)#来源和发送给谁，使用外键
    mtime = models.DateTimeField(auto_now_add=True)
    mtitle = models.CharField(max_length = 100)
    minfo = models.TextField()

class CourseMessageStatus(models.Model):
    mno = models.ForeignKey('CourseMessage', on_delete = models.CASCADE)
    sno = models.ForeignKey('Student', on_delete = models.CASCADE)
    cno = models.ForeignKey('Course', on_delete = models.CASCADE)
    status = models.BooleanField(default = False)

#lzy部分课程资源等
class CourseResource(models.Model):
    rno = models.AutoField(primary_key=True)  # 资源编号
    cname = models.ForeignKey(Course, on_delete=models.CASCADE)  # 关联课程
    rname = models.CharField(max_length=100)  # 资源名称
    rdesc = models.CharField(max_length=500, blank=True, null=True)  # 资源描述
    rfile = models.CharField(max_length=200)  # 资源文件地址（存储在OSS）
    upload_time = models.DateTimeField(auto_now_add=True)  # 上传时间

    def __str__(self):
        return self.rname

class ResourceProgress(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)  # 学生
    resource = models.ForeignKey(CourseResource, on_delete=models.CASCADE)  # 课程资源
    progress = models.CharField(max_length=100)  # 记录进度，可能是时间戳或页码，具体根据文件类型

    def __str__(self):
        return f"{self.student.username} - {self.resource.rname} - {self.progress}"

#留的作业
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # 关联的课程
    title = models.CharField(max_length=100)  # 作业标题
    description = models.TextField()  # 作业描述
    assignment_file = models.CharField(max_length=200, blank=True, null=True)  # 作业附件
    due_date = models.DateTimeField()  # 截止日期
    isMutualAssessment = models.BooleanField(default=False) #是否是互评
    allowDelaySubmission = models.BooleanField(default=False) #是否能补交
    delay_date = models.DateField(blank=True, null=True, default=None) #补交最晚截止时间 不设置则可以一直提交
    maxGrade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=100) #作业满分

    def __str__(self):
        return self.title

#提交作业
class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)  # 关联的作业
    student = models.ForeignKey('Student', on_delete=models.CASCADE)  # 提交学生
    submission_text = models.TextField(blank=True, null=True)  # 作业文本
    submission_file = models.CharField(max_length=200, blank=True, null=True)  # 文件地址（存储在OSS）
    submitted_at = models.DateTimeField(auto_now_add=True)  # 提交时间
    delay_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=None)#延迟交作业的周数，0-不限
    grade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=100)

    def __str__(self):
        return f"{self.student.sname} - {self.assignment.title}"
