from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import chatRoom
from eduPlatform import settings
from login.models import User
from . import models
from .models import ChooseClass, Course
from chatRoom.models import Favorite
from .serializers import courseSerializer, courseDetailSerializer
from chatRoom.serializers import FavoriteSerializer

import jwt


def extract_user_info_from_auth(request):
    auth_head = request.headers.get('Authorization')

    # 检查 Authorization 头是否存在
    if not auth_head:
        raise AuthenticationFailed('Authorization header is missing.')

    # 尝试提取 token
    try:
        token = auth_head.split()[1]
    except IndexError:
        raise AuthenticationFailed('Invalid Authorization header format. Expected format: "Bearer <token>"')

    # 尝试解码 JWT
    try:
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded_payload['user_id']
        user_type = decoded_payload['userType']

        return user_id, user_type  # 返回用户 ID 和用户类型
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token.')

# Create your views here.
class StudentHomePageView(APIView):
    def get(self, request):

        user_id, user_type = extract_user_info_from_auth(request)
        sno = User.objects.get(pk=user_id).username
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
        user_id, user_type = extract_user_info_from_auth(request)
        tno = User.objects.get(pk=user_id).username

        courses_data = Course.objects.filter(tno_id=tno)

        # 使用序列化器将课程数据转换为可返回的格式
        ser = courseSerializer(courses_data, many=True)
        return Response({"code": 200, "data": ser.data})


class GetUsername(APIView):#获取用户名
    permission_classes = [IsAuthenticated]  # 确保只有经过身份验证的用户可以访问该接口

    def get(self, request):
        user_id, user_type = extract_user_info_from_auth(request)

        # 获取用户名
        user = User.objects.get(pk=user_id)
        username = user.username
        return Response({'username': username,'userType':user_type})


class GetCourseDetails(APIView):
    def get(self, request,course_id):
        try:
            course_ob = models.Course.objects.get(cno=course_id)
            ser = courseDetailSerializer(course_ob, many=False)
            return Response({"code":200,"data":ser.data})
        except Course.DoesNotExist:
            return Response({'error':'课程未找到'},status=status.HTTP_404_NOT_FOUND)

def update_course_intro(request, course_no):
    try:
        course = Course.objects.get(course_no=course_no)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    # 获取新的课程介绍
    new_intro = request.data.get('cintro', None)
    if new_intro is not None:
        course.cintro = new_intro
        course.save()

    # 返回更新后的课程数据
    serializer = courseSerializer(course)
    return Response(serializer.data, status=status.HTTP_200_OK)

class Favorites(APIView):
    def get(self, request):
        user_id, user_type = extract_user_info_from_auth(request)
        print(user_id)
        favorites = chatRoom.models.Favorite.objects.filter(userNo=user_id)
        ser = FavoriteSerializer(favorites, many=True)

        return Response({"code":200,"data":ser.data})

    def post(self, request,dno):
        user_id, user_type = extract_user_info_from_auth(request)
        existing_favorite = chatRoom.models.Favorite.objects.filter(userNo=user_id, dno=dno).first()
        if existing_favorite:
            return Response({'detail': '已经收藏此帖子了'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            discussion = chatRoom.models.Discussion.objects.get(dno=dno)
            user = User.objects.get(pk=user_id)
        except chatRoom.models.Discussion.DoesNotExist:
            return Response({'detail':'讨论不存在'},status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'detail':'用户不存在'},status=status.HTTP_404_NOT_FOUND)

        favorite = chatRoom.models.Favorite.objects.create(userNo=user, dno=discussion)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request,dno):
        user_id, user_type = extract_user_info_from_auth(request)
        favorite = chatRoom.models.Favorite.objects.get(userNo=user_id, dno=dno).delete()
        return Response({"code": 200, "message": '收藏已经成功删除'})


