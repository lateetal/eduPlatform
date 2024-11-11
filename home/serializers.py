from rest_framework import serializers

from homepage.models import Student,Teacher
from login.models import User


class StudentSerializer(serializers.ModelSerializer):
    userType = serializers.SerializerMethodField()
    class Meta:
        model = Student
        fields = '__all__'
    def get_userType(self, obj):
        return 'student'

class TeacherSerializer(serializers.ModelSerializer):
    userType = serializers.SerializerMethodField()
    class Meta:
        model = Teacher
        fields = '__all__'
    def get_userType(self, obj):
        return 'teacher'