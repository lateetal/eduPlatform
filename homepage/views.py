import time
import oss2
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from eduPlatform import settings
from login.models import User
from . import models
from .models import ChooseClass, Course, CourseMessage, Teacher, CourseMessageStatus, CourseResource, Assignment
from chatRoom.models import Favorite
from .serializers import courseSerializer, courseDetailSerializer, CourseMessageSerializer, \
    CourseMessageStatusSerializer, StudentSerializer, CourseResourceSerializer, AssignmentSerializer
from chatRoom.serializers import FavoriteSerializer

from zhipuai import ZhipuAI
import jwt
from multipart import MultipartParser

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

class UpdateCourseIntro(APIView):
    def put(self, request, course_no):
        try:
            course = Course.objects.get(cno=course_no)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        # 获取新的课程介绍
        new_intro = request.data.get('cintro')
        if new_intro is not None:
            course.cintro = new_intro
            course.save()
        else:
            return Response({'error': 'No new course introduction provided'}, status=status.HTTP_400_BAD_REQUEST)

        # 返回更新后的课程数据
        serializer = courseDetailSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AIchat(APIView):
    def post(self, request):
        client = ZhipuAI(api_key="2272f57760983b79497d3941b37b9cdc.deE7EZflxBR8gEJV")  # 请填写您自己的APIKey
        # 从请求中获取用户输入
        user_input = request.data.get('input')

        response = client.chat.asyncCompletions.create(
            model="glm-4",  # 填写需要调用的模型名称
            messages=[
                {
                    "role": "user",
                    "content": user_input
                }
            ],
        )

        # 获取响应ID
        task_id = response.id
        task_status = ''
        get_cnt = 0

        # 轮询获取结果
        while task_status != 'SUCCESS' and task_status != 'FAILED' and get_cnt < 40:
            time.sleep(2)  # 等待2秒后再查询
            result_response = client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
            task_status = result_response.task_status

            if task_status == 'SUCCESS':
                generated_content = result_response.choices[0].message.content
                return Response({'message': generated_content}, status=status.HTTP_200_OK)
            elif task_status == 'FAILED':
                return Response({'error': '任务失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            get_cnt += 1

        return Response({'error': '请求超时，请稍后再试'}, status=status.HTTP_408_REQUEST_TIMEOUT)


#两个展示场景 要写两个类
class CourseMessagesView(APIView):
    def get(self, request,course_id):
        user_id, user_type = extract_user_info_from_auth(request)
        username = User.objects.get(pk=user_id).username
        if user_type == 'teacher':
            message = CourseMessage.objects.filter(mcourse_id=course_id)
            ser = CourseMessageSerializer(message, many=True)
        else:
            message = CourseMessageStatus.objects.filter(sno_id=username, cno=course_id)
            ser = CourseMessageStatusSerializer(message, many=True)
        return Response({"code":200,"data":ser.data})

        # 只有教师能发送消息
    def post(self, request, course_id):
        try:
            user_id, user_type = extract_user_info_from_auth(request)
            tno = User.objects.get(pk=user_id).username
            mtitle = request.data.get('title')
            minfo = request.data.get('info')
            students = ChooseClass.objects.filter(cno_id=course_id)

            if not students.exists():
                return Response({"code": 404, "message": "No students found."}, status=status.HTTP_404_NOT_FOUND)

            message = CourseMessage.objects.create(
                    mtime=timezone.now(),
                    mcourse_id=course_id,
                    msend_id=tno,
                    mtitle=mtitle,
                    minfo=minfo,
                )
            message.save()


            for student in students:
                print(student.sno_id)
                messageStatus = CourseMessageStatus.objects.create(
                    mno_id = message.mno,
                    sno_id = student.sno_id,
                    cno_id = course_id,
                )
                messageStatus.save()
            return Response({"code": 200, "message": "Messages sent successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"code": 500, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 删除消息
    def delete(self, request, course_id):
        try:
            mno = request.data.get('mno')
            message = CourseMessage.objects.filter(mno=mno)
            message.delete()

            return Response({"code": 200, "message": "Message deleted successfully."},
                            status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({"code": 500, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllCourseMessage(APIView):
    def get(self, request):
        user_id, user_type = extract_user_info_from_auth(request)
        username = User.objects.get(pk=user_id).username
        # 展示老师教授课程的通知
        if user_type == 'teacher':
            messages = CourseMessage.objects.filter(msend_id=username)
            ser = CourseMessageSerializer(messages, many=True)
        else:
            # 获取学生选的所有课程
            messages = CourseMessageStatus.objects.filter(sno_id=username)
            ser = CourseMessageStatusSerializer(messages, many=True)
        return Response({"code": 200, "data": ser.data})

class AllStudent(APIView):
    def get(self, request,course_id):
        # 查找选定课程的所有学生
        try:
            selected_students = ChooseClass.objects.filter(cno__cno=course_id).select_related('sno')
            if not selected_students.exists():
                return Response({"code": 404, "message": "没有选课学生"})

            # 提取学生信息
            students = [choose_class.sno for choose_class in selected_students]
            serializer = StudentSerializer(students, many=True)
            return Response({"code": 200, "data": serializer.data})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#lzy部分
# 课程资源列表视图
class CourseResourceListView(APIView):
    def get(self, request, course_id):
        try:
            # 使用课程ID获取对应的课程
            course = models.Course.objects.get(cno=course_id)
            # 获取关联的课程资源
            resources = models.CourseResource.objects.filter(cname_id=course)
            if not resources.exists():
                return Response({'message': 'No resources found for this course'}, status=status.HTTP_404_NOT_FOUND)

            # 序列化课程资源
            serializer = CourseResourceSerializer(resources, many=True)
            return Response({'code': 200, 'data': serializer.data})
        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


# 教师上传资源视图 实现上传和删除
class UploadResourceView(APIView):
    permission_classes = [IsAuthenticated]  # 确保只有经过身份验证的用户可以上传资源

    def post(self, request, course_id):
        try:
            user_id, user_type = extract_user_info_from_auth(request)
            # 获取对应的课程
            course = models.Course.objects.get(cno=course_id)

            # 检查用户权限，确保是教师用户
            try:
                tno = User.objects.get(pk=user_id).username
                teacher = models.Teacher.objects.get(tno=tno)  # 使用教师工号作为用户ID
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
                    return Response({'error': f'File upload failed: {str(e)}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

            return Response({'message': 'Resource uploaded successfully!', 'resource_id': resource.rno},
                            status=status.HTTP_201_CREATED)

        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self,request, course_id):
        # 没写用户身份验证，靠前端
        rno = request.data.get('rno', None)
        #删除阿里云oss文件
        file_path = CourseResource.objects.get(pk=rno).rfile
        bucket.delete_object(file_path)
        CourseResource.objects.get(pk=rno).delete()


        return Response({'code': 200, 'message': '课程资源文件删除成功' })

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
    def get(self, request, course_id, assignment_id):
        try:
            assignment = models.Assignment.objects.get(id=assignment_id, course_id=course_id)
            serializer = AssignmentSerializer(assignment, many=False)
            return Response({'code': 200, 'data': serializer.data})
        except models.Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)


# 作业提交视图 实现了重复提交只保留最新的记录
class AssignmentSubmissionView(APIView):
    # parser_classes = [MultipartParser]  # 解析多部分文件上传
    permission_classes = [IsAuthenticated]  # 确保只有经过身份验证的用户可以提交作业

    def post(self, request, course_id, assignment_id):
        try:
            # 获取对应的作业
            assignment = models.Assignment.objects.get(id=assignment_id)
            try:
                user_id, user_type = extract_user_info_from_auth(request)
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
            submission_text = request.data.get('submission_text', '')
            print(submission_text)
            submission_file = request.FILES.get('submission_file', None)

            # 查找是否已有提交记录
            try:
                existing_submission = models.AssignmentSubmission.objects.get(assignment=assignment, student=student)
                # 如果已经存在提交记录，删除阿里云上的旧文件
                if existing_submission.submission_file:
                    try:
                        old_file_path = existing_submission.submission_file
                        bucket.delete_object(old_file_path)  # 删除OSS中的旧文件
                    except Exception as e:
                        print(f"Failed to delete old file from OSS: {str(e)}")
                        return Response({'error': f'Failed to delete old file: {str(e)}'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 更新提交记录中的文本和文件
                existing_submission.submission_text = submission_text
                if submission_file:
                    # 上传新的文件到阿里云OSS
                    try:
                        new_file_name = f"assignment/submissions/{assignment_id}/{submission_file.name}"
                        bucket.put_object(new_file_name, submission_file)  # 确保 bucket 已正确初始化
                        existing_submission.submission_file = new_file_name  # 更新文件路径
                    except Exception as e:
                        print(f"OSS upload failed: {str(e)}")
                        return Response({'error': f'File upload failed: {str(e)}'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 保存修改后的提交记录
                existing_submission.save()
                return Response({'message': 'Assignment updated successfully!', 'id': existing_submission.id},
                                status=status.HTTP_200_OK)

            except models.AssignmentSubmission.DoesNotExist:
                # 如果没有提交记录，创建新的提交记录
                file_path = None
                if submission_file:
                    try:
                        file_name = f"assignment/submissions/{assignment_id}/{submission_file.name}"
                        bucket.put_object(file_name, submission_file)  # 确保 bucket 是正确初始化的
                        file_path = file_name  # 生成 OSS 中的文件路径
                    except Exception as e:
                        print(f"OSS upload failed: {str(e)}")
                        return Response({'error': f'File upload failed: {str(e)}'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 创建新的作业提交记录
                submission = models.AssignmentSubmission.objects.create(
                    assignment=assignment,
                    student=student,
                    submission_text=submission_text,
                    submission_file=file_path
                )
                submission.save()

                return Response({'message': 'Assignment submitted successfully!', 'id': submission.id},
                                status=status.HTTP_201_CREATED)

        except models.Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 教师布置作业视图 以及修改和删除
class CreateAssignmentView(APIView):
    # parser_classes = [MultipartParser]  # 解析多部分文件上传 why
    permission_classes = [IsAuthenticated]  # 确保只有经过身份验证的用户可以布置作业

    def post(self, request, course_id):
        try:
            # 获取对应的课程
            course = models.Course.objects.get(cno=course_id)

            user_id, user_type = extract_user_info_from_auth(request)
            # 检查用户权限，确保是教师用户
            try:
                tno = User.objects.get(pk=user_id).username
                teacher = models.Teacher.objects.get(tno=tno)  # 使用教师工号作为用户ID
            except models.Teacher.DoesNotExist:
                return Response({'error': 'Only teachers can create assignments.'}, status=status.HTTP_403_FORBIDDEN)
            # 解析表单数据
            title = request.data.get('title', '')
            description = request.data.get('description', '')
            start_date = request.data.get('start_date','')
            due_date = request.data.get('due_date', '')
            isMutualAssessment = request.data.get('isMutualAssessment', False)
            allowDelaySubmission = request.data.get('allowDelaySubmission', False)
            delayDate = request.data.get('delayDate', None)
            maxGrade = request.data.get('maxGrade', 100)


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
                    return Response({'error': f'File upload failed: {str(e)}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # 创建新的作业记录
            assignment = models.Assignment.objects.create(
                course=course,
                title=title,
                description=description,
                assignment_file=file_path,
                due_date=due_date,
                start_date=start_date,
                isMutualAssessment=isMutualAssessment,
                allowDelaySubmission = allowDelaySubmission,
                delay_date = delayDate,
                maxGrade = maxGrade
            )
            assignment.save()
            return Response({'message': 'Assignment created successfully!', 'assignment_id': assignment.id},
                            status=status.HTTP_201_CREATED)
        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #删除布置的作业
    def delete(self, request, course_id):
        assignment_id = request.data.get('assignment_id', None)

        assignment = models.Assignment.objects.get(id=assignment_id)
        bucket.delete_object(assignment.assignment_file)

        Assignment.objects.filter(id=assignment_id).delete()
        return Response({'message': '作业成功删除'},
                        status=status.HTTP_201_CREATED)

    #修改布置的作业
    def put(self, request, course_id):
        try:
            assignment_id = request.data.get('assignment_id', None)
            assignment = models.Assignment.objects.get(id=assignment_id)

            # 更新作业的其他信息
            title = request.data.get('title', assignment.title)
            description = request.data.get('description', assignment.description)
            due_date = request.data.get('due_date', assignment.due_date)
            start_date = request.data.get('start_date', assignment.start_date)
            isMutualAssessment = request.data.get('isMutualAssessment', assignment.isMutualAssessment)
            allowDelaySubmission = request.data.get('allowDelaySubmission', assignment.allowDelaySubmission)
            delayDate = request.data.get('delayDate', assignment.delay_date)
            maxGrade = request.data.get('maxGrade', assignment.maxGrade)

            # 处理文件上传，若有新文件则替换旧文件
            assignment_file = request.FILES.get('assignment_file', None)
            if assignment_file:
                # 删除原文件
                if assignment.assignment_file:
                    bucket.delete_object(assignment.assignment_file)

                # 上传新文件
                try:
                    file_name = f"course/assignments/{course_id}/{assignment_file.name}"
                    bucket.put_object(file_name, assignment_file)
                    assignment.assignment_file = file_name
                except Exception as e:
                    return Response({'error': f'File upload failed: {str(e)}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 更新作业记录
            assignment.title = title
            assignment.description = description
            assignment.start_date = start_date
            assignment.due_date = due_date
            assignment.isMutualAssessment = isMutualAssessment
            assignment.allowDelaySubmission = allowDelaySubmission
            assignment.delay_date = delayDate
            assignment.maxGrade = maxGrade
            assignment.save()

            return Response({'message': 'Assignment updated successfully!', 'assignment_id': assignment.id},
                            status=status.HTTP_200_OK)

        except models.Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#课程日历和大纲的上传和下载
class uploadInfoFileView(APIView):
    def post(self, request, course_id, file_type):
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 获取文件名和扩展名
        file_name = uploaded_file.name  # e.g., "0001-outline.pdf"
        if file_type == 'outline':
            file_path = f"course/outline/{file_name}"
        else:
            file_path = f"course/calendar/{file_name}"
          # 阿里云存储路径

        # 获取文件内容
        file_content = uploaded_file.read()

        try:
            # 尝试获取课程信息
            course = Course.objects.get(pk=course_id)

            if file_type == 'outline':
                old_file_path = course.coutline
            else:
                old_file_path = course.calender

            if old_file_path:
                try:
                    bucket.delete_object(old_file_path[1:])
                except oss2.exceptions.NoSuchKey:
                    pass  # 如果文件不存在，忽略错误

            # 上传新文件到阿里云 OSS
            bucket.put_object(file_path, file_content)

            # 更新数据库中的文件路径
            if file_type == 'outline':
                course.coutline = f'/{file_path}'
            else:
                course.calender = f'/{file_path}'
            course.save()

            return Response({'code': 200})

        except ObjectDoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        except oss2.exceptions.OssError as e:
            return Response({"error": f"OSS Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



