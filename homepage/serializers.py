from rest_framework import serializers
from homepage.models import Teacher, Course, CourseMessage, CourseMessageStatus, Student, CourseResource, Assignment, \
    AssignmentSubmission


class courseSerializer(serializers.Serializer):
    cno = serializers.CharField()
    cname = serializers.CharField()
    course_no = serializers.CharField()
    course_class = serializers.CharField()
    picAddr = serializers.CharField()

    # def update(self, instance, validated_data):
    #     instance.name
    # 更新图片，能够上传图片以及保存图片所在的文件位置。

class courseTeacherDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'
        # exclude = ['email']  # 将 'email' 字段排除在外
        # fields = ['id', 'name']  序列化部分
        # 不添加则序列化全部

#嵌套序列化器 包括序列化教师字段
class courseDetailSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = '__all__'

    def get_teacher(self, obj):
        try:
            print(obj.tno_id)
            teacher = Teacher.objects.get(tno=obj.tno_id)
            return courseTeacherDetailSerializer(teacher).data
        except Teacher.DoesNotExist:
            return None

class CourseMessageSerializer(serializers.ModelSerializer):
    coursename = serializers.CharField(source='course.cname', read_only=True)

    class Meta:
        model = CourseMessage
        fields = ('mno', 'mcourse', 'msend', 'mtime', 'mtitle', 'minfo', 'coursename')

class CourseMessageStatusSerializer(serializers.ModelSerializer):
    # 嵌套序列化器用于获取 CourseMessage 的字段
    mno = serializers.PrimaryKeyRelatedField(queryset=CourseMessage.objects.all())
    mtime = serializers.DateTimeField(source='mno.mtime', read_only=True)
    mtitle = serializers.CharField(source='mno.mtitle', read_only=True)
    minfo = serializers.CharField(source='mno.minfo', read_only=True)
    coursename = serializers.CharField(source='course.cname', read_only=True)
    status = serializers.BooleanField()

    class Meta:
        model = CourseMessageStatus
        fields = ['mno', 'mtime', 'mtitle', 'minfo', 'coursename', 'status']

#lzy部分学生课程资源作业部分
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class CourseResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseResource
        fields = ['rno', 'rname', 'rdesc', 'rfile', 'upload_time']
        #fields = ['rno', 'rname', 'rdesc', 'upload_time']

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_id', 'assignment', 'student', 'submission_text', 'submission_file', 'submission_time']