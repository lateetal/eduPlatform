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
    start_date = models.DateTimeField(blank=True, null=True, default=None)  # 作业开始提交的时间
    due_date = models.DateTimeField()  # 截止日期
    isMutualAssessment = models.BooleanField(default=False) #是否是互评
    allowDelaySubmission = models.BooleanField(default=False) #是否能补交
    delay_date = models.DateTimeField(blank=True, null=True, default=None) #补交最晚截止时间 不设置则可以一直提交
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
    delay_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=None)#延迟交作业的天数，0-不限
    grade = models.IntegerField(validators=[MinValueValidator(-1), MaxValueValidator(100)], default=-1)
    delay_grade = models.IntegerField(validators=[MinValueValidator(-1), MaxValueValidator(100)], default=-1)#延迟交作业的成绩

    mutual_assessments_done = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.student.sname} - {self.assignment.title}"

#互评作业表
class MutualAssessment(models.Model):
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)  # 关联的作业
    student = models.ForeignKey('Student', on_delete=models.CASCADE)  # 提交互评的学生
    to_assess_student = models.ForeignKey('Student', related_name='assessments', on_delete=models.CASCADE)  # 被评的学生
    grade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True,
                                blank=True)  # 评定成绩
    feedback = models.TextField(blank=True, null=True)  # 评语
    assessed_at = models.DateTimeField(auto_now_add=True)  # 提交互评时间
    is_assessed = models.BooleanField(default=False)

    def __str__(self):
        return f"Assessment by {self.student} for {self.to_assess_student} - {self.assignment.title}"

    class Meta:
        unique_together = ('assignment', 'student', 'to_assess_student')

#教师批改作业
class TeacherAssignment(models.Model):
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)  # 关联的作业
    AssignmentSubmission = models.ForeignKey('AssignmentSubmission', on_delete=models.CASCADE)
    grade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True,
                                blank=True)  # 评定成绩
    feedback = models.TextField(blank=True, null=True)  # 评语
    assessed_at = models.DateTimeField(auto_now_add=True)  # 提交互评时间
    showFeedback = models.BooleanField(default=False)


# 文件夹
class Folder(models.Model):
    folder_name = models.CharField(max_length=100)  # 文件夹名称
    folder_desc = models.CharField(max_length=500, blank=True, null=True)  # 文件夹描述

    def __str__(self):
        return self.folder_name


# 课件
class CourseResource_ppt(models.Model):
    rno = models.AutoField(max_length=10, primary_key=True)  # 资源编号
    cname = models.ForeignKey(Course, on_delete=models.CASCADE)  # 关联课程
    rname = models.CharField(max_length=100)  # 资源名称
    rdesc = models.CharField(max_length=500, blank=True, null=True)  # 资源描述
    rfile = models.CharField(max_length=200)  # 资源文件地址（存储在OSS）
    upload_time = models.DateTimeField(auto_now_add=True)  # 上传时间
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, blank=True, null=True)  # 关联文件夹

    def __str__(self):
        return self.rname


# 试题库
class CourseResource_test(models.Model):
    rno = models.AutoField(max_length=10, primary_key=True)  # 资源编号
    cname = models.ForeignKey(Course, on_delete=models.CASCADE)  # 关联课程
    rname = models.CharField(max_length=100)  # 资源名称
    rdesc = models.CharField(max_length=500, blank=True, null=True)  # 资源描述
    rfile = models.CharField(max_length=200)  # 资源文件地址（存储在OSS）
    upload_time = models.DateTimeField(auto_now_add=True)  # 上传时间
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, blank=True, null=True)  # 关联文件夹

    def __str__(self):
        return self.rname

# 习题库
class Question(models.Model):
    QUESTION_TYPES = (
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('subjective', '主观题'),
    )
    DIFFICULTY_LEVELS = (
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    )
    # 题目类型
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single_choice')
    # 难易程度
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    # 考察的知识点
    knowledge_point = models.CharField(max_length=200)
    # 题目内容
    content = models.TextField()
    # 选项内容（单选题和多选题）
    options = models.JSONField(blank=True, null=True)  # 存储选项内容的JSON格式，例如：{"A": "选项A", "B": "选项B", ...}
    # 正确答案（单选题和多选题）
    correct_answer = models.CharField(max_length=200, blank=True, null=True)  # 存储正确答案的选项字母，例如："A" 或 "A,B"
    # 答案解析
    answer_explanation = models.TextField(blank=True, null=True)
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 关联的课程
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return f"{self.question_type} - {self.content[:50]}"
