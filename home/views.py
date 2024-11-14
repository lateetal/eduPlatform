from tabnanny import check

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.db.migrations import serializer
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from home.serializers import StudentSerializer, TeacherSerializer
from homepage.models import Student,Teacher
from homepage.views import extract_user_info_from_auth
from login.models import User


# Create your views here.

class HomeView(APIView):
    def get(self, request,userNo):
        user_id, user_type = extract_user_info_from_auth(request)
        if userNo == '0':
            username = User.objects.get(id=user_id).username
        else:
            username = User.objects.get(username=userNo).username
            user_type = User.objects.get(username=userNo).user_type

        if user_type == 'student':
            student = Student.objects.get(pk=username)
            ser = StudentSerializer(student, context={'user_id':user_id})
        else:
            teacher = Teacher.objects.get(pk=username)
            ser = TeacherSerializer(teacher, context={'user_id':user_id})
        return Response({"code":200,"data":ser.data})

class modifyInformation(APIView):
    def put(self, request):
        user_id, user_type = extract_user_info_from_auth(request)
        username = User.objects.get(id=user_id).username  # 获取用户名


        # 根据用户类型选择是处理学生还是教师
        if user_type == 'student':
            # 获取学生对象
            student = Student.objects.get(pk=username)
            new_Smail = request.data.get('mail')
            student.smail = new_Smail
            student.save()
            # 将请求的数据传递给学生序列化器进行更新
            ser = StudentSerializer(student)  # partial=True 允许部分更新
            return Response({"code": 200, "data": ser.data})

        elif user_type == 'teacher':
            # 获取教师对象
            teacher = Teacher.objects.get(pk=username)

            new_Tmail = request.data.get('mail')
            new_Toffice = request.data.get('office')
            new_Tphone = request.data.get('phone')
            new_Tintro = request.data.get('intro')

            teacher.tmail = new_Tmail
            teacher.toffice = new_Toffice
            teacher.tphone = new_Tphone
            teacher.tintro = new_Tintro

            teacher.save()
            ser = TeacherSerializer(teacher)  # partial=True 允许部分更新
            return Response({"code":200,"data":ser.data})

        # 验证数据是否有效
        if serializer.is_valid():
            # 保存更新后的数据
            serializer.save()
            # 返回更新后的数据
            return Response({"code": 200, "data": serializer.data})
        else:
            # 如果验证失败，返回错误信息
            return Response(serializer.errors)

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
