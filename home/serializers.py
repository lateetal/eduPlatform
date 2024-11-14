from rest_framework import serializers

from chatRoom.models import Favorite, Follow
from homepage.models import Student,Teacher
from login.models import User


class StudentSerializer(serializers.ModelSerializer):
    userType = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'
    def get_userType(self, obj):
        return 'student'
    def get_is_followed(self, obj):
        user_id = self.context.get('user_id') #当前用户的id
        username = User.objects.get(pk=user_id).username
        if username == obj.sno:
            return True
        other_user_id = User.objects.get(username=obj.sno).pk
        if Follow.objects.filter(fan_id=user_id, followed_id=other_user_id).exists():
            return True
        else:
            return False

class TeacherSerializer(serializers.ModelSerializer):
    userType = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = '__all__'
    def get_userType(self, obj):
        return 'teacher'
    def get_is_followed(self, obj):
        user_id = self.context.get('user_id') #当前用户的id
        username = User.objects.get(pk=user_id).username
        if username == obj.tno:
            return True
        other_user_id = User.objects.get(username=obj.tno).pk
        if Follow.objects.filter(fan_id=user_id, followed_id=other_user_id).exists():
            return True
        else:
            return False