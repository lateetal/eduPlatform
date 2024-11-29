#homepage 测试用例
#1-365
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

import homepage
import login
from chatRoom.models import User, Review, Discussion, Like, DiscussionLike, atMessage, Favorite, Topic
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

#StudentHomePageView
def test_StudentHomePageView(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('studenthomepage')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

def test_TeacherHomePageView(client,load_db_data):
    access_token = get_access_token(client, '001', password)
    url = reverse('teacherhomepage')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

def test_GetUsername(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('getusername')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

def test_GetCourseDetails(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('course-detail',args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

    url = reverse('course-detail', args=['1111'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == '课程未找到'

def test_UpdateCourseIntro(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('update_course_intro', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'cintro':'new introduction',
    }
    response = client.put(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

    url = reverse('update_course_intro', args=['1111'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.put(url)

    # 验证响应
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == 'Course not found'

    url = reverse('update_course_intro', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.put(url)

    # 验证响应
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == 'No new course introduction provided'

def test_AIchat(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('aichat')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'input':'你好'
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

def test_get_CourseMessagesView(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('messagesView', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

    access_token = get_access_token(client, '001', password)
    url = reverse('messagesView', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

def test_post_CourseMessagesView(client, load_db_data):
    access_token = get_access_token(client, '001', password)
    url = reverse('messagesView', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'title':'标题',
        'info':'正文'
    }
    response = client.post(url,data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == 'Messages sent successfully.'

def test_delete_CourseMessagesView(client, load_db_data):

    access_token = get_access_token(client, username, password)
    url = reverse('messagesView',args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'mno':1
    }
    response = client.delete(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.data['message'] == 'Message deleted successfully.'

def test_AllCourseMessage(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('messagesView')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    access_token = get_access_token(client, '001', password)
    url = reverse('messagesView')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

def test_AllStudent(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('studentView',args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

def test_get_ResourseFolder(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_folder', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

def test_post_ResourseFolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_folder', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'folderPath':'/5/',
        'folderName':'newfilepath',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '文件夹创建成功'

def test_delete_ResourseFolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_folder', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'folderId':5
    }
    response = client.delete(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '文件夹删除成功'

def test_get_ResourseFile(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_file',args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'rno':7
    }
    response = client.get(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK

def test_post_ResourseFile(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_file',args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # 创建一个模拟文件
    test_file = SimpleUploadedFile("test_file.txt", b"Test file content", content_type="text/plain")

    data = {
        'folderPath': 14,
        'rname': 'file name',
        'resourceFile': test_file,
    }

    # 模拟OSS文件上传
    with patch('homepage.views.bucket.put_object') as mock_put_object:
        mock_put_object.return_value = None  # 模拟上传成功

        # 发起POST请求
        response = client.post(url, data, format='multipart')

    # 断言响应状态码和消息
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == 'Resource uploaded successfully!'

def test_delete_ResourseFile(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('resources_file',args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'rno':9
    }
    response = client.delete(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Resource deleted successfully!'

    data = {
        'rno': 100
    }
    response = client.delete(url, data, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == 'Resource not found.'









