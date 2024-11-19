from rest_framework import serializers
from homepage.models import Teacher, Course, CourseMessage, CourseMessageStatus, Student, Assignment, \
    AssignmentSubmission, Folder, CourseResource_ppt, CourseResource_test, Question, TeacherAssignment, ChooseClass


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

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['folder_name', 'folder_desc']

class CourseResourceSerializer_ppt(serializers.ModelSerializer):
    class Meta:
        model = CourseResource_ppt
        fields = ['rno', 'rname', 'rdesc', 'rfile', 'upload_time',"folder"]

class CourseResourceSerializer_test(serializers.ModelSerializer):
    class Meta:
        model = CourseResource_test
        fields = ['rno', 'rname', 'rdesc', 'rfile', 'upload_time',"folder"]

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    studentNum = serializers.SerializerMethodField()
    submitNum = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = '__all__'
    def get_studentNum(self, obj):
        studentNum = ChooseClass.objects.filter(cno_id=obj.course_id).count()
        return studentNum
    def get_submitNum(self, obj):
        submitNum = AssignmentSubmission.objects.filter(assignment_id=obj.pk).count()
        return submitNum



class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'student', 'submission_text', 'submission_file', 'submitted_at']

class TeacherAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAssignment
        fields = '__all__'

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.sname')  # Assuming 'sname' is the field name for student's name

    class Meta:
        model = AssignmentSubmission
        fields = [
            'student_id', 'student_name', 'submission_text', 'submission_file',
            'submitted_at', 'delay_time', 'grade'
        ]
        read_only_fields = ['student_id', 'student_name', 'submission_text', 'submission_file', 'submitted_at', 'delay_time', 'grade']

#课程文件序列化
class courseResource_pptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseResource_ppt
        fields = '__all__'

#文件夹序列化
class FolderSerializer(serializers.ModelSerializer):
    # 文件夹中的资源，使用 courseResource_pptSerializer 进行序列化
    resources = serializers.SerializerMethodField()  # 文件夹下的资源
    subfolders = serializers.SerializerMethodField()  # 子文件夹

    class Meta:
        model = Folder
        fields = ['id', 'folder_name', 'folderPathInSql', 'resources', 'subfolders']

    def get_resources(self, obj):
        resources = CourseResource_ppt.objects.filter(rfileInSql=obj)
        return courseResource_pptSerializer(resources, many=True).data

    def get_subfolders(self, obj):
        subfolder_path_prefix = f"{obj.folderPathInSql}{obj.id}/"  # 构建子文件夹路径前缀
        subfolders = Folder.objects.filter(folderPathInSql=subfolder_path_prefix)
        return FolderSerializer(subfolders, many=True).data