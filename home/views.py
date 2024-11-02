from tabnanny import check

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from home.serializers import StudentSerializer, TeacherSerializer
from homepage.models import Student,Teacher
from homepage.views import extract_user_info_from_auth
from login.models import User


# Create your views here.

class HomeView(APIView):
    def get(self, request):
        user_id, user_type = extract_user_info_from_auth(request)
        username = User.objects.get(id=user_id).username

        if user_type == 'student':
            student = Student.objects.get(pk=username)
            ser = StudentSerializer(student)
        else:
            teacher = Teacher.objects.get(pk=username)
            ser = TeacherSerializer(teacher)
        return Response({"code":200,"data":ser.data})


class Password(APIView):
    def post(self, request):
        user_id, user_type = extract_user_info_from_auth(request)
        oldPassword = request.data.get('oldPassword')
        newPassword = request.data.get('newPassword')
        confirmPassword = request.data.get('confirmPassword')

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"code": 404, "data": {"error": "用户不存在"}}, status=404)

        # 验证旧密码
        if not check_password(oldPassword, user.password):
            return Response({"code": 400, "data": {"error": "旧密码不正确"}}, status=400)

        # 验证新密码是否一致
        if newPassword != confirmPassword:
            return Response({"code": 400, "data": {"error": "两次输入的新密码不同"}}, status=400)

        # 更新密码
        user.set_password(newPassword)
        user.save()
        update_session_auth_hash(request, user)

        return Response({"code": 200, "data": {'success': '密码修改成功'}}, status=200)
