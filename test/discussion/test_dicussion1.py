#测试chatRoom showDiscussion

import pytest
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User

import login
from chatRoom.models import Discussion, Course
from rest_framework.test import APIClient

from login import models


@pytest.fixture
@pytest.mark.django_db
def user():
    user, created = models.User.objects.get_or_create(username='22301080', password='password',user_type='student')
    return user

@pytest.fixture
@pytest.mark.django_db
def course():
    course, created = Course.objects.get_or_create(pk='0001', name='Test Course')
    return course

@pytest.mark.django_db
@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_show_discussion(client, user):
    # 使用现有用户和课程来进行测试
    url = reverse('discussionShow', args=['0001'])
    client.force_authenticate(user=user)  # 模拟认证
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'data' in response.data
    assert len(response.data['data']) > 0

