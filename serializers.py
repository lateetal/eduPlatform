from rest_framework import serializers
from homepage.models import Assignment, AssignmentSubmission, CourseResource, Teacher, Course


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
        

class CourseResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseResource
        fields = ['rno', 'rname', 'rdesc', 'rfile', 'upload_time']
        #fields = ['rno', 'rname', 'rdesc', 'upload_time']



class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date','assignment_file']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_id', 'assignment', 'student', 'submission_text', 'submission_file', 'submission_time']