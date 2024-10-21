from django.utils import timezone

import jwt
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from chatRoom.models import Discussion, Review
from chatRoom.serializers import discussionSerializer, ReviewSerializer
from eduPlatform import settings
import boto3

class UploadImageView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        oss_client = boto3.client('oss',
                                  aws_access_key_id=settings.OSS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.OSS_ACCESS_KEY_SECRET,
                                  endpoint_url=settings.OSS_ENDPOINT)
        try:
            oss_client.upload_fileobj(file, settings.OSS_BUCKET_NAME, file.name)
            url = f"{settings.OSS_ENDPOINT}/{settings.OSS_BUCKET_NAME}/{file.name}"
            return Response({'url': url})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# Create your views here.
class showDiscussion(APIView):
    def get(self, request,course_id):
        try:
            discussion = Discussion.objects.filter(cno_id=course_id)
            ser = discussionSerializer(discussion, many=True)
            return Response({"code":200,"data":ser.data})
        except Discussion.DoesNotExist:
            return Response({'error':'课程未找到'},status=status.HTTP_404_NOT_FOUND)

    def post(self,request,course_id):#新建讨论
        title = request.data['dtitle']
        info = request.data['dinfo']

        auth_head = request.headers.get('Authorization')
        token = auth_head.split()[1]
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        owner_id = decoded_payload['user_id']

        print(owner_id)

        if not title or not info:
            return Response({'error': '标题和内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_discussion = Discussion.objects.create(dtitle=title,dinfo=info,
                                                       postTime=timezone.now(),updateTime=timezone.now(),
                                                       cno_id=course_id,ownerNo_id=owner_id)
            ser = discussionSerializer(new_discussion)
            return Response({"code":200,"data":ser.data})

        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self,request,course_id,dno):
        try:
            discussion = Discussion.objects.filter(dno=dno)
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


