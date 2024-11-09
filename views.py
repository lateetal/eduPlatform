from multipart import FormParser, MultipartParser
import oss2
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
from .serializers import AssignmentSerializer, CourseResourceSerializer, courseSerializer, courseDetailSerializer
from chatRoom.serializers import FavoriteSerializer

import jwt

accessKeyId = 'LTAI5tAtNfQg5VqN22gT3Tsn'
accessKeySecret = 'Mqha28ubnHLtRlZaaDhXiqz6O9Xnwf'
auth = oss2.Auth(accessKeyId, accessKeySecret)
endpoint = 'oss-cn-beijing.aliyuncs.com'
bucket = oss2.Bucket(auth, endpoint, 'edu-platform-2024')


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

    def post(self, request, dno):
        user_id, user_type = extract_user_info_from_auth(request)

        # 检查用户是否已经收藏
        existing_favorite = Favorite.objects.filter(userNo=user_id, dno=dno).first()
        if existing_favorite:
            # 如果已存在，则删除该收藏
            existing_favorite.delete()
            return Response({"code": 200, "message": '收藏已经成功删除'})

        # 如果不存在，则继续处理创建逻辑
        try:
            discussion = chatRoom.models.Discussion.objects.get(dno=dno)
            user = User.objects.get(pk=user_id)
        except chatRoom.models.Discussion.DoesNotExist:
            return Response({"code": 404, "message": '讨论不存在'})
        except User.DoesNotExist:
            return Response({"code": 404, "message": '用户不存在'})

        # 创建 Favorite 实例
        favorite = Favorite.objects.create(userNo=user, dno=discussion)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#课程资源列表视图
class CourseResourceListView(APIView):
    def get(self, request, course_id):
        try:
            # 使用课程ID获取对应的课程
            course = models.Course.objects.get(cno=course_id)
            # 获取关联的课程资源
            resources = models.CourseResource.objects.filter(cname_id=course )
            if not resources.exists():
                return Response({'message': 'No resources found for this course'}, status=status.HTTP_404_NOT_FOUND)

        # 序列化课程资源
            serializer = CourseResourceSerializer(resources, many=True)
            return Response({'code': 200, 'data': serializer.data})
        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
# 教师上传资源视图
class UploadResourceView(APIView):
    permission_classes = [IsAuthenticated]  # 确保只有经过身份验证的用户可以上传资源

    def post(self, request, course_id):
        try:
            # 获取对应的课程
            course = models.Course.objects.get(cno=course_id)

            # 从 Authorization 头中获取 token 并解码
            auth_head = request.headers.get('Authorization')
            if not auth_head:
                return Response({'error': 'Authorization header is missing.'}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                token = auth_head.split()[1]
                decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_payload['user_id']
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_401_UNAUTHORIZED)

            # 检查用户权限，确保是教师用户
            try:
                teacher = models.Teacher.objects.get(tno=user_id)  # 使用教师工号作为用户ID
            except models.Teacher.DoesNotExist:
                return Response({'error': 'Only teachers can upload resources.'}, status=status.HTTP_403_FORBIDDEN)

            # 解析表单数据
            resource_name = request.data.get('resource_name', '')
            resource_description = request.data.get('resource_description', '')
            resource_file = request.FILES.get('resource_file', None)

            # 如果有文件，上传到阿里云OSS
            if resource_file:
                try:
                    file_name = f"course/resources/{course_id}/{resource_file.name}"
                    bucket.put_object(file_name, resource_file)  # 确保 bucket 是正确初始化的
                    file_path = file_name  # 生成 OSS 中的文件路径
                except Exception as e:
                    print(f"OSS upload failed: {str(e)}")  # 打印详细错误信息
                    return Response({'error': f'File upload failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

            # 创建新的课程资源记录
            resource = models.CourseResource.objects.create(
                cname=course,
                rname=resource_name,
                rdesc=resource_description,
                rfile=file_path
            )
            resource.save()

            return Response({'message': 'Resource uploaded successfully!', 'resource_id': resource.rno}, status=status.HTTP_201_CREATED)

        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
# 作业列表视图
class AssignmentListView(APIView):
    def get(self, request, course_id):
        try:
            # 获取对应的课程
            course = models.Course.objects.get(cno=course_id)
            # 获取课程下的所有作业
            assignments = models.Assignment.objects.filter(course_id=course_id)
            if not assignments.exists():
                return Response({'message': 'No assignments found for this course'}, status=status.HTTP_404_NOT_FOUND)

            # 序列化作业
            serializer = AssignmentSerializer(assignments, many=True)
            return Response({'code': 200, 'data': serializer.data})
        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

# 作业详情视图
class AssignmentDetailView(APIView):
    def get(self, request,course_id, assignment_id):
        try:
            assignment = models.Assignment.objects.get(id=assignment_id,course_id=course_id)
            serializer = AssignmentSerializer(assignment, many=False)
            return Response({'code': 200, 'data': serializer.data})
        except models.Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)

# 作业提交视图
class AssignmentSubmissionView(APIView):
    parser_classes = [MultipartParser]  # 解析多部分文件上传
    permission_classes = [IsAuthenticated]  # 确保只有经过身份验证的用户可以提交作业

    def post(self, request, course_id, assignment_id):
        try:
            # 获取对应的作业
            assignment = models.Assignment.objects.get(id=assignment_id)

            # 从 Authorization 头中获取 token 并解码
            auth_head = request.headers.get('Authorization')
            if not auth_head:
                return Response({'error': 'Authorization header is missing.'}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                token = auth_head.split()[1]
                decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_payload['user_id']
                student_sno = User.objects.get(pk=user_id).username  # 使用获取到的用户名作为学号
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            # 获取对应的学生
            try:
                student = models.Student.objects.get(sno=student_sno)  # 使用sno来查找学生
            except models.Student.DoesNotExist:
                return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

            # 获取提交的作业文本和文件
            submission_text = request.POST.get('submission_text', '')
            print(submission_text)
            submission_file = request.FILES.get('submission_file', None)

            # 如果有文件，上传到阿里云OSS
            file_path = None
            if submission_file:
                try:
                    file_name = f"assignment/submissions/{assignment_id}/{submission_file.name}"
                    bucket.put_object(file_name, submission_file)  # 确保 bucket 是正确初始化的
                    file_path = file_name  # 生成 OSS 中的文件路径
                except Exception as e:
                    print(f"OSS upload failed: {str(e)}")  # 打印详细错误信息
                    return Response({'error': f'File upload failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    print(f"General Error: {str(e)}")  # Log other errors
                    return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 创建新的作业提交记录
            submission = models.AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student,
                submission_text=submission_text,
                submission_file=file_path
            )
            submission.save()

            return Response({'message': 'Assignment submitted successfully!', 'id': submission.id}, status=status.HTTP_201_CREATED)

        except models.Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#教师布置作业视图      
class CreateAssignmentView(APIView):
    parser_classes = [MultipartParser]  # 解析多部分文件上传
    permission_classes = [IsAuthenticated]  # 确保只有经过身份验证的用户可以布置作业
    def post(self, request, course_id):
        try:
            # 获取对应的课程
            course = models.Course.objects.get(cno=course_id)
            # 从 Authorization 头中获取 token 并解码
            auth_head = request.headers.get('Authorization')
            if not auth_head:
                return Response({'error': 'Authorization header is missing.'}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                token = auth_head.split()[1]
                decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_payload['user_id']
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_401_UNAUTHORIZED)
            # 检查用户权限，确保是教师用户
            try:
                teacher = models.Teacher.objects.get(tno=user_id)  # 使用教师工号作为用户ID
            except models.Teacher.DoesNotExist:
                return Response({'error': 'Only teachers can create assignments.'}, status=status.HTTP_403_FORBIDDEN)
            # 解析表单数据
            title = request.data.get('title', '')
            description = request.data.get('description', '')
            due_date = request.data.get('due_date', '')
            assignment_file = request.FILES.get('assignment_file', None)
            # 如果有文件，上传到阿里云OSS
            file_path = ''
            if assignment_file:
                try:
                    file_name = f"course/assignments/{course_id}/{assignment_file.name}"
                    bucket.put_object(file_name, assignment_file)  # 确保 bucket 是正确初始化的
                    file_path = file_name  # 生成 OSS 中的文件路径
                except Exception as e:
                    print(f"OSS upload failed: {str(e)}")  # 打印详细错误信息
                    return Response({'error': f'File upload failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # 创建新的作业记录
            assignment = models.Assignment.objects.create(
                course=course,
                title=title,
                description=description,
                assignment_file=file_path,
                due_date=due_date
            )
            assignment.save()
            return Response({'message': 'Assignment created successfully!', 'assignment_id': assignment.id}, status=status.HTTP_201_CREATED)
        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


