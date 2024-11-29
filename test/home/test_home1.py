
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

def test_HomeView(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('home', args=['0'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    access_token = get_access_token(client, '001', password)
    url = reverse('home', args=['0'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

def test_modifyInformation(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('modifyInfo')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'mail':'1916771180@qq.com'
    }
    response = client.put(url,data)

    assert response.status_code == status.HTTP_200_OK

    access_token = get_access_token(client, '001', password)
    url = reverse('modifyInfo')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'mail': '1916771180@qq.com',
        'office':'office',
        'phone':'phone',
        'intro':'intro',
    }
    response = client.put(url,data)

    assert response.status_code == status.HTTP_200_OK

def Password(client,load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('updatePassword')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    data = {
        'oldPassword':'123456',
        'newPassword':'123',
        'confirmPassword':'123'
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK




