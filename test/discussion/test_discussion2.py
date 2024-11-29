import time

import pytest
from django.core.management import call_command
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

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

#Like 点赞review
def test_Like_Review(client, load_db_data):
    #成功点赞和成功取消点赞测试
    access_token = get_access_token(client, username, password)
    url = reverse('likeReview', args=['2'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    # 发起 GET 请求
    response = client.post(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '点赞成功'


    response = client.post(url)
    assert response.data['message'] == '取消点赞成功'

    #失败测试
    access_token = get_access_token(client, username, password)
    url = reverse('likeReview', args=['5'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == '回复未找到'

#DiscussionLikeView
def test_Like_Discussion(client, load_db_data):
    #成功点赞和成功取消点赞测试
    access_token = get_access_token(client, username, password)
    url = reverse('likeDiscussion', args=['12'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.post(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '点赞成功'


    response = client.post(url)
    assert response.data['message'] == '取消点赞成功'

    #失败测试
    access_token = get_access_token(client, username, password)
    url = reverse('likeReview', args=['999'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == '回复未找到'

#FavoritesFolderLike
def test_Like_FavoritesFolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('likeFolder')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'fno': '3',
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '点赞成功'

    response = client.post(url, data, format='json')
    assert response.data['message'] == '取消点赞成功'

#AtMessageView
def test_get_atMessageView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('atMessage')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证
    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

#修改消息已读否
def test_post_atMessageView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('atMessage')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    message = atMessage.objects.create(rno_id = 2 ,senderno_id='7',receiverno_id='6',sendTime='2024-11-28 13:44:57.311000',status=False)

    data = {
        'messageId':message.pk
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '消息已读'

#FavoriteFolder
def test_get_FavoriteFolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('allFolder', args=['0'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

    access_token = get_access_token(client, username, password)
    url = reverse('allFolder', args=['001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

def test_post_FavoriteFolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('allFolder', args=['001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.post(url)

    # 验证响应
    assert response.data['message'] == '无权限新建收藏夹'

    access_token = get_access_token(client, username, password)
    url = reverse('allFolder', args=[0])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'fname': '收藏',
        'fstatus': True
    }
    response = client.post(url,data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '收藏夹创建成功'

def test_delete_FavoriteFolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('allFolder', args=['001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.delete(url)

    # 验证响应
    assert response.data['message'] == '无权限删除收藏夹'

    access_token = get_access_token(client, username, password)
    url = reverse('allFolder', args=['0'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'fname': '默认收藏夹',
    }
    response = client.delete(url, data, format='json')

    # 验证响应

    assert response.status_code == status.HTTP_200_OK


def test_put_FavoriteFolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('allFolder', args=['001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.put(url)

    # 验证响应
    assert response.data['message'] == '无权限修改收藏夹'

    access_token = get_access_token(client, username, password)
    url = reverse('allFolder', args=['0'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'fno':'3',
        'fname': '收藏夹',
        'fstatus': True
    }
    response = client.put(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '收藏夹修改成功'

#FavoriteFolderDetail
def test_get_FavoriteFolderDetail(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('folderDetail', args=['3'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

def test_post_FavoriteFolderDetail(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('folderDetail', args=['3'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'dno':'14',
    }
    response = client.post(url,data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '帖子收藏成功'

    access_token = get_access_token(client, username, password)
    url = reverse('folderDetail', args=['3'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'dno': '12',
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.data['message'] == '该帖子已被收藏过了'

def test_delete_FavoriteFolderDetail(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('folderDetail', args=['3'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    favourite = Favorite.objects.create(dno_id = 14,fno_id = 3)
    data = {
        'dno': 14
    }
    response = client.delete(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '帖子收藏删除成功'

def test_put_FavoriteFolderDetail(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('folderDetail', args=['3'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证
    data = {
        'dno': 12,
        'newFno': 4
    }
    response = client.put(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '帖子收藏移动成功'

#otherfolder
def test_post_otherfolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('collectOtherFolder')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'fno': 5
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == '不能收藏本人收藏夹'

    data = {
        'fno': 100
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == '未找到该收藏夹'

    data = {
        'fno': 4
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['message'] == '该收藏夹已经被收藏过了'

    data = {
        'fno': 3
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.data['message'] == '已经成功收藏别人的收藏夹'

def test_delete_otherfolder(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('collectOtherFolder')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'fno': 4
    }
    response = client.delete(url, data, format='json')
    assert response.data['message'] == '已取消收藏该收藏夹'

#showTopic
def test_get_showTopic(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('showTopic', args=['0001'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    Topic.objects.create(tname='作业')

    data = {
        'topic':'作业'
    }
    response = client.get(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

#followerView
def test_get_followerView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('follower')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证
    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

def test_post_followerView(client, load_db_data):
    access_token = get_access_token(client, '001', password)
    url = reverse('follower')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'follower':'001'
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.data['message'] == '不能关注自己'

    data = {
        'follower': '22301002'
    }
    response = client.post(url, data, format='json')

    # 验证响应
    assert response.data['message'] == '关注成功'

def test_delete_followerView(client, load_db_data):
    access_token = get_access_token(client, '001', password)
    url = reverse('follower')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    data = {
        'follower':'22301080'
    }
    response = client.delete(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '取关成功'

#fanView
def test_get_fanView(client, load_db_data):
    access_token = get_access_token(client, username, password)
    url = reverse('fan')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证
    response = client.get(url)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK


def test_delete_fanView(client, load_db_data):
    access_token = get_access_token(client, '001', password)
    url = reverse('fan')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')  # 使用 token 进行身份验证

    message = atMessage.objects.create(rno_id=2, senderno_id='7', receiverno_id='6',
                                       sendTime='2024-11-28 13:44:57.311000', status=False)

    data = {
        'fan':'003'
    }
    response = client.delete(url, data, format='json')

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '移除粉丝成功'















