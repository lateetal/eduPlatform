from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from eduPlatform import settings
from login.models import User
from . import models
from .models import ChooseClass, Course
from .serializers import courseSerializer, courseDetailSerializer

import jwt

# Create your views here.
class StudentHomePageView(APIView):
    def get(self, request):
        auth_head = request.headers.get('Authorization')
        if auth_head:
            try:
                token = auth_head.split()[1]
                decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_payload['user_id']
                sno = User.objects.get(pk=user_id).username

            except jwt.ExpiredSignatureError:

                return Response({"code": 401, "message": "Token has expired."}, status=401)

            except jwt.InvalidTokenError:

                return Response({"code": 401, "message": "Invalid token."}, status=401)
        else:
            return Response({"code": 401, "message": "Authorization header missing."}, status=401)

        # 查询该学生所选的所有课程
        chosen_classes = ChooseClass.objects.filter(sno__sno=sno).select_related('cno')

        # 检查是否找到课程
        if not chosen_classes.exists():
            return Response({"code": 404, "message": "No courses found for the given student number."}, status=404)

        # 提取课程信息
        courses_data = [course.cno for course in chosen_classes]  # 获取课程对象

        # 使用序列化器将课程数据转换为可返回的格式
        ser = courseSerializer(courses_data, many=True)
        return Response({"code":200,"data":ser.data})

class TeacherHomePageView(APIView): #教师展示
    def get(self, request):
        auth_head = request.headers.get('Authorization')

        if auth_head:
            try:
                token = auth_head.split()[1]
                decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_payload['user_id']
                tno = User.objects.get(pk=user_id).username


            except jwt.ExpiredSignatureError:

                return Response({"code": 401, "message": "Token has expired."}, status=401)

            except jwt.InvalidTokenError:

                return Response({"code": 401, "message": "Invalid token."}, status=401)
        else:
            return Response({"code": 401, "message": "Authorization header missing."}, status=401)

        courses_data = Course.objects.filter(tno_id=tno)

        # 使用序列化器将课程数据转换为可返回的格式
        ser = courseSerializer(courses_data, many=True)
        return Response({"code": 200, "data": ser.data})


class GetUsername(APIView):#获取用户名
    permission_classes = [IsAuthenticated]  # 确保只有经过身份验证的用户可以访问该接口

    def get(self, request):
        auth_head = request.headers.get('Authorization')

        # 检查 Authorization 头是否存在
        if not auth_head:
            raise AuthenticationFailed('Authorization header is missing.')

        # 尝试提取 token
        try:
            token = auth_head.split()[1]
        except IndexError:
            raise AuthenticationFailed('Invalid Authorization header format. Expected format: "Bearer <token>"')

        try:
            # 解码 JWT
            decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_payload['user_id']
            userType = decoded_payload['userType']

            print(userType)

            # 获取用户名
            user = User.objects.get(pk=user_id)
            username = user.username

            return Response({'username': username,'userType':userType})
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')



class GetCourseDetails(APIView):
    def get(self, request,course_id):
        try:
            course_ob = models.Course.objects.get(cno=course_id)
            ser = courseDetailSerializer(course_ob, many=False)
            return Response({"code":200,"data":ser.data})
        except Course.DoesNotExist:
            return Response({'error':'课程未找到'},status=status.HTTP_404_NOT_FOUND)


