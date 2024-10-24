import os
import uuid

import oss2
from django.http import JsonResponse
from django.utils import timezone

import jwt
from django.shortcuts import render
from oss2.defaults import connect_timeout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

import chatRoom
from chatRoom import models
from chatRoom.models import Discussion, Review, PictureReview, PictureDisscussion,Like
from chatRoom.serializers import discussionSerializer, ReviewSerializer
from eduPlatform import settings

from homepage.views import extract_user_info_from_auth
from login.models import User


class showDiscussion(APIView):
    def get(self, request,course_id):
        try:
            discussion = Discussion.objects.filter(cno_id=course_id)
            ser = discussionSerializer(discussion, many=True)
            return Response({"code":200,"data":ser.data})
        except Discussion.DoesNotExist:
            return Response({'error':'课程未找到'},status=status.HTTP_404_NOT_FOUND)

    def post(self, request, course_id):
        title = request.data.get('title')
        info = request.data.get('content')
        images = request.data.get('images')

        # 验证标题和内容是否为空
        if not title or not info:
            return Response({'error': '标题和内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取用户信息
        owner_id, user_type = extract_user_info_from_auth(request)

        # 创建讨论
        try:
            havePic = 1 if images else 0

            new_discussion = Discussion.objects.create(
                dtitle=title,
                dinfo=info,
                postTime=timezone.now(),
                updateTime=timezone.now(),
                havePic=havePic,
                cno_id=course_id,
                ownerNo_id=owner_id
            )
            ser = discussionSerializer(new_discussion)
            if images:
                for image in images:
                    index = image.find("/course")
                    if index != -1:
                        cutImage = image[index:]  # 从/cours
                    picture = PictureDisscussion.objects.create(
                        dno=new_discussion,  # 将新讨论实例关联到图片
                        pfile=cutImage  # 假设 image 是已经上传并保存的图片文件路径
                    )

            return Response({"code": 200, "data": ser.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self,request,course_id,dno):
        try:
            discussion = Discussion.objects.get(dno=dno)
            if discussion.havePic == 1:
                PictureDisscussion.objects.filter(dno=dno).delete()

            discussion.delete()
            return Response({"code":200,"message":'讨论已经成功删除'})

        except Discussion.DoesNotExist:
            return Response({'error': '讨论未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self,request,course_id,dno):
        discussion = get_object_or_404(Discussion, dno=dno)
        discussion.dtitle = request.data['dtitle']
        discussion.dinfo = request.data['dinfo']

        discussion.save()
        return Response({"code":200,"message":'讨论已经成功编辑'})

class showReview(APIView):
    def get(self, request,course_id,dno):
        try:
            discussion = Discussion.objects.get(dno=dno)
            reviews = Review.objects.filter(dno_id=dno)
            disSer = discussionSerializer(discussion)
            disData = disSer.data
            disData['reviews'] = ReviewSerializer(reviews,many = True).data

            return Response({"code":200,"data":disData})

        except Discussion.DoesNotExist:
            return Response({'error':'课程未找到'},status=status.HTTP_404_NOT_FOUND)

    def post(self,request,course_id,dno):
        info = request.data.get('content')
        images = request.data.get('images')

        if not info:
            return Response({'error': '内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        owner_id, user_type = extract_user_info_from_auth(request)



        # 创建讨论
        try:
            havePic = 1 if images else 0

            new_review = Review.objects.create(
                rinfo=info,
                postTime=timezone.now(),
                likeNum=0,
                havePic=havePic,
                isTop=0,
                dno_id=dno,
                ownerNo_id=owner_id
            )
            ser = ReviewSerializer(new_review)
            discussion = Discussion.objects.get(dno=dno)
            discussion.updateTime = timezone.now()
            serDiscussion = discussionSerializer(discussion)

            if images:
                for image in images:
                    index = image.find("/course")
                    if index != -1:
                        cutImage = image[index:]  # 从/cours
                    picture = PictureReview.objects.create(
                        rno=new_review,  # 将新讨论实例关联到图片
                        pfile=cutImage  # 假设 image 是已经上传并保存的图片文件路径
                    )

            return Response({"code": 200, "data": ser.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self,request,course_id,dno,rno):
        try:
            review = Review.objects.get(rno=rno)
            if review.havePic == 1:
                PictureReview.objects.filter(rno=rno).delete()
            review.delete()
            return Response({"code": 200, "message": '回复已经成功删除'})

        except Discussion.DoesNotExist:
            return Response({'error': '讨论未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Like(APIView):
    def post(self, request, rno):
        # 提取用户信息
        user_id, user_type = extract_user_info_from_auth(request)

        # 尝试获取用户和评论
        try:
            user = User.objects.get(pk=user_id)
            review = chatRoom.models.Review.objects.get(rno=rno)
        except User.DoesNotExist:
            return Response({'error': '用户未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Review.DoesNotExist:
            return Response({'error': '回复未找到'}, status=status.HTTP_404_NOT_FOUND)

        # 检查用户是否已经点赞
        existing_like = chatRoom.models.Like.objects.filter(userNo=user, rno=review).first()

        if existing_like:
            # 如果存在，则删除点赞
            existing_like.delete()
            return Response({'message': '取消点赞成功'}, status=status.HTTP_200_OK)
        else:
            # 如果不存在，则创建新的点赞
            new_like = models.Like.objects.create(userNo=user, rno=review)
            return Response({'message': '点赞成功'}, status=status.HTTP_201_CREATED)

