from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from isort.literal import assignment
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

import homepage
import login
from chatRoom.models import User, Review, Discussion, Like, DiscussionLike, atMessage, Favorite, Topic
from homepage.models import TeacherAssignment, Assignment, MutualAssessment
from login import models

# 用户凭证
username = '22301080'
password = '123456'

def get_access_token(client, username, password):
    token_url = reverse('token_obtain_pair')  # 获取 token 的 URL

    response = client.post(token_url, {
        'username': username,
        'password': password,
    })

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data  # 确保返回数据中有 access token
    return response.data['access']

# 创建一个加载数据的fixture
@pytest.fixture(scope='function')
def load_db_data(db):
    # 通过 call_command 加载 data.json 文件到临时数据库
    call_command('loaddata', 'data.json')

# 提供 APIClient 实例
@pytest.fixture
def client():
    return APIClient()

def test_get_AssignmentListView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('assignment-list',args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    url = reverse('assignment-list', args=['1111'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_AssignmentView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('oneAssignment',args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')


    data = {
        'assignment_id':'12'
    }
    response = client.get(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK

def test_AssignmentDetailView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('assignment-detail',args=['0001',11])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

def test_StudentSubmissionDetailView(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('student-submission-detail', args=['0001','12','22301080'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    url = reverse('student-submission-detail', args=['0001', '1111', '22301080'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    url = reverse('student-submission-detail', args=['0001', '12', '1000'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == 'Submission not found'

def test_get_TeacherAssignmentView(client, load_db_data):
    teacherAssignment =TeacherAssignment.objects.create(grade=6,feedback='vv',showFeedback=True,assignment_id=12,AssignmentSubmission_id=13)

    access_token = get_access_token(client, username, password)
    url = reverse('TeacherAssignment', args=['0001','12','22301080'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

def test_post_TeacherAssignmentView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('TeacherAssignment',args=['0001','12','22301080'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')


    data = {
        'grade':6,
        'feedback': '加油',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['detail'] == '作业批改成功'

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == '作业更新成功'

    data = {
        'grade': 'wee',
        'feedback': '加油',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == '成绩必须是有效的数字'

    data = {
        'grade': '10000',
        'feedback': '加油',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_AssignmentSubmissionView(client, load_db_data):
    # 获取有效的访问令牌
    access_token = get_access_token(client, username, password)
    url = reverse('assignment-submit', args=['0001', 12])

    # 设置认证信息
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')


    # 模拟提交的数据（包含作业文本和文件）
    data = {
        'submission_text': 'This is a test submission.',
        'submission_file': open('D:/大学/大二 下/人工智能/1-AI概述.pdf', 'rb')  # 注意：此处需要用真实文件路径来测试
    }

    # 发送 POST 请求，提交作业
    response = client.post(url, data, format='multipart')

    # 检查响应是否为成功状态
    assert response.status_code == status.HTTP_205_RESET_CONTENT
    assert response.data['error'] == 'You cannot submit this assignment, the deadline has passed.'  # 假设成功时返回这个信息

    url = reverse('assignment-submit', args=['0001', 13])

    # 设置认证信息
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # 发送 POST 请求，提交作业
    response = client.post(url, data, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == 'Assignment submitted successfully!'  # 假设成功时返回这个信息


def test_assignment_not_found(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('assignment-submit', args=['0001', 999])

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    data = {'submission_text': 'Test submission', 'submission_file': None}

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == 'Assignment not found.'

def test_post_CreateAssignmentView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('create-assignment', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.post(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['error'] == 'Only teachers can create assignments.'

    access_token = get_access_token(client, '001', password)
    url = reverse('create-assignment', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'title':'title',
        'description':'description',
        'start_date':'2024-11-14 12:13:00.000000',
        'due_date':'2024-11-20 12:13:00.000000',
        'maxGrade':10,
        'assignment_file': open('D:/大学/大二 下/人工智能/1-AI概述.pdf', 'rb')  # 注意：此处需要用真实文件路径来测试
    }
    response = client.post(url,data, format='multipart')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == 'Assignment created successfully!'

def test_delete_CreateAssignmentView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('create-assignment', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'assignment_id':'8',
    }
    response = client.delete(url,data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == '作业成功删除'

def test_put_CreateAssignmentView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('create-assignment', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'assignment_id':8,
        'title': 'title',
        'description': 'description',
        'start_date': '2024-11-14 12:13:00.000000',
        'due_date': '2024-11-20 12:13:00.000000',
        'maxGrade': 10,
        'assignment_file': open('D:\\大学\\大二 下\\人工智能\\2-知识表示与知识图谱.pdf', 'rb')  # 注意：此处需要用真实文件路径来测试
    }
    response = client.put(url, data, format='multipart')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Assignment updated successfully!'

def test_generateMutualAssessment(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('generateMutualAssessment', args=['12'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    MutualAssessment.objects.all().delete()

    response = client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '互评任务发布成功'

    access_token = get_access_token(client, username, password)
    url = reverse('generateMutualAssessment', args=['13'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.post(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == '作业提交人数过少，无法生成互评'

def test_get_MutualAssessmentView(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('mutualAssessment',args=['12'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    access_token = get_access_token(client, '001', password)
    url = reverse('mutualAssessment', args=['12'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == '没有互评记录'

def test_post_MutualAssessmentView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('mutualAssessment',args=['12'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')


    data = {
        'toAssessStudentId':'22301000',
        'grade':5,
        'feedback':'feedback',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '评分成功'

    data = {
        'toAssessStudentId': '22301000',
        'grade':'www',
        'feedback': 'feedback',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == '成绩必须是有效的数字'

    data = {
        'toAssessStudentId': '22301000',
        'grade': 10000,
        'feedback': 'feedback',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_uploadInfoFileView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('upload_file', args=['0001','outline'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
         'file': open('D:/大学/大二 下/人工智能/1-AI概述.pdf', 'rb')  # 注意：此处需要用真实文件路径来测试
    }
    response = client.post(url, data, format='multipart')


    assert response.status_code == status.HTTP_200_OK

    url = reverse('upload_file', args=['0001', 'calendar'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'file': open('D:/大学/大二 下/人工智能/1-AI概述.pdf', 'rb')  # 注意：此处需要用真实文件路径来测试
    }
    response = client.post(url, data, format='multipart')

    assert response.status_code == status.HTTP_200_OK

def test_get_courseResourceListView_test(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_test', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

def test_post_courseResourceListView_test(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_test', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'resource_name':'文件名',
        'resource_description':'描述',
        'resource_file': open('D:/大学/大二 下/人工智能/1-AI概述.pdf', 'rb')  # 注意：此处需要用真实文件路径来测试
    }
    response = client.post(url,data,format='multipart')


    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == 'Resource uploaded successfully!'

    data = {
        'resource_name': '文件名',
        'resource_description': '描述',
        }
    response = client.post(url, data, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == 'No file uploaded.'

def test_delete_courseResourceListView_test(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_test', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'rno':9
    }
    response = client.delete(url,data,format='multipart')

    assert response.data['message'] == '课程资源文件删除成功'

def test_get_CourseQuestionListView(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_question', args=['0001','all'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

def test_post_CourseQuestionListView(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_question', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        "question_type": "主观题",
        "difficulty": "hard",
        "knowledge_point": "计算机网络-网络协议",
        "content": "请简述OSI七层模型的各层功能。",
        "options": 'null',
        "correct_answer": 'null',
        "answer_explanation": "OSI七层模型包括物理层、数据链路层、网络层、传输层、会话层、表示层和应用层，每一层都有不同的功能，旨在提供标准化的网络通信。"
    }
    response = client.post(url,data,format='multipart')

    assert response.status_code == status.HTTP_201_CREATED

def test_delete_CourseQuestionListView(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_question', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'id':5
    }
    response = client.delete(url,data)

    assert response.status_code == status.HTTP_200_OK

def test_getAllSubmit(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('getAllSubmit', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK









