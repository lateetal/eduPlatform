#测试chatRoom showDiscussion
#基础讨论和回复测试
import pytest
import pymysql
from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User

import login
from chatRoom.models import Discussion, Course
from rest_framework.test import APIClient

from login import models

# 用户凭证
username = '22301080'
password = '123456'

# 获取访问 token 的辅助函数
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

# showDiscussion
def test_show_discussion(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('discussionShow', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    # 发起 GET 请求
    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert 'data' in response.data
    assert len(response.data['data']) > 0

def test_create_discussion(client, load_db_data):
    # 获取 access token
    access_token = get_access_token(client, username, password)

    # 使用 access token 进行认证
    url = reverse('discussionShow', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    # 准备 POST 请求数据
    data = {
        'title': 'Test Discussion Title',
        'content': 'This is the content of the test discussion.',
        'images': []  # 如果有图片，可以模拟图片路径或上传图片
    }

    # 发起 POST 请求
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_201_CREATED
    assert 'data' in response.data
    assert response.data['code'] == 200
    assert response.data['data']['dtitle'] == 'Test Discussion Title'
    assert response.data['data']['dinfo'] == 'This is the content of the test discussion.'

def test_delete_discussion(client, load_db_data):
    # 获取 access token
    access_token = get_access_token(client, username, password)

    # 使用 access token 进行认证
    url = reverse('discussionDelete', args=['0001', 12])  # 传递课程ID和讨论ID
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    # 发起 DELETE 请求
    response = client.delete(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['code'] == 200
    assert response.data['message'] == '讨论已经成功删除'

def test_update_discussion(client, load_db_data):
    # 获取 access token
    access_token = get_access_token(client, username, password)

    # 使用 access token 进行认证
    url = reverse('discussionDelete', args=['0001', 14])  # 传递课程ID和讨论ID
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    # 准备 PUT 请求数据
    data = {
        'dtitle': 'Updated Discussion Title',
        'dinfo': 'This is the updated content of the test discussion.'
    }

    # 发起 PUT 请求
    response = client.put(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['code'] == 200
    assert response.data['message'] == '讨论已经成功编辑'

    # 确保讨论数据已更新
    discussion = Discussion.objects.get(dno=14)  # 使用实际的讨论ID
    assert discussion.dtitle == 'Updated Discussion Title'
    assert discussion.dinfo == 'This is the updated content of the test discussion.'

#filterDiscussion
def test_filter_discussion(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('discussionFilter', args=['0001'])  # 传递链接对应变量
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    keyword = '讨论'
    data = {
        'keyword':keyword,
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['code'] == 200

    discussions = response.data['data']
    assert isinstance(discussions, list)

    for discussion in discussions:
        assert keyword in discussion['dtitle'] or keyword in discussion['dinfo']

#showReview
def test_show_reviews(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('reviewShow', args=['0001','12'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'data' in response.data
    assert len(response.data['data']) > 0

def test_create_reviews(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('reviewShow', args=['0001', '12'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # 准备 POST 请求数据
    data = {
        'content': 'Test review',
    }

    # 发起 POST 请求
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_201_CREATED
    assert 'data' in response.data
    assert response.data['code'] == 200
    assert response.data['data']['rinfo'] == 'Test review'

def test_delete_review(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('reviewDelete', args=['0001',12 , 2])  # 传递课程ID和讨论ID
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    # 发起 DELETE 请求
    response = client.delete(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['code'] == 200
    assert response.data['message'] == '回复已经成功删除'

#filterReview
def test_filter_review(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('reviewFilter', args=['0001','12'])  # 传递链接对应变量
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    keyword = 'Test'
    data = {
        'keyword': keyword,
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['code'] == 200
