from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import chatRoom
from chatRoom import models
from chatRoom.models import Discussion, Review, PictureReview, PictureDisscussion, Like, atMessage
from chatRoom.serializers import discussionSerializer, ReviewSerializer, AtMessageSerializer
from homepage.views import extract_user_info_from_auth
from login.models import User
import re
from django.db import transaction


class showDiscussion(APIView):
    def get(self, request,course_id):
        try:
            user_id, user_type = extract_user_info_from_auth(request)
            discussion = Discussion.objects.filter(cno_id=course_id)
            ser = discussionSerializer(discussion, context={'user_id':user_id}, many=True)
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
    def get(self, request, course_id, dno):
        try:
            user_id, user_type = extract_user_info_from_auth(request)
            discussion = Discussion.objects.get(dno=dno)
            reviews = Review.objects.filter(dno_id=dno)
            disSer = discussionSerializer(discussion)
            disData = disSer.data
            disData['reviews'] = ReviewSerializer(reviews, context={'user_id': user_id}, many=True).data

            return Response({"code": 200, "data": disData})

        except Discussion.DoesNotExist:
            return Response({'error': '课程未找到'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, course_id, dno):
        info = request.data.get('content')
        images = request.data.get('images')

        if not info:
            return Response({'error': '内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        owner_id, user_type = extract_user_info_from_auth(request)

        try:
            havePic = 1 if images else 0

            # 创建新的回复
            new_review = Review.objects.create(
                rinfo=info,
                postTime=timezone.now(),
                likeNum=0,
                havePic=havePic,
                isTop=0,
                dno_id=dno,
                ownerNo_id=owner_id
            )

            # 处理图片
            if images:
                for image in images:
                    index = image.find("/course")
                    if index != -1:
                        cutImage = image[index:]  # 假设 image 是已上传的图片路径
                    picture = PictureReview.objects.create(
                        rno=new_review,  # 将新讨论实例关联到图片
                        pfile=cutImage  # 假设 image 是已上传并保存的图片文件路径
                    )

            # 解析 @ 用户并创建 atMessage
            self._process_at_users(info, new_review)

            ser = ReviewSerializer(new_review)
            discussion = Discussion.objects.get(dno=dno)
            discussion.updateTime = timezone.now()
            serDiscussion = discussionSerializer(discussion)

            return Response({"code": 200, "data": ser.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, course_id, dno, rno):
        try:
            review = Review.objects.get(rno=rno)

            # 删除相关的 atMessage 记录
            at_messages = atMessage.objects.filter(rno=rno)
            at_messages.delete()

            # 删除图片
            if review.havePic == 1:
                PictureReview.objects.filter(rno=rno).delete()

            review.delete()

            return Response({"code": 200, "message": '回复已经成功删除'})

        except Review.DoesNotExist:
            return Response({'error': '回复未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_at_users(self, content, review):
        print("in _process_at_users")
        # 使用正则表达式提取 @ 后面的用户名
        mentioned_users = re.findall(r'@(\w+)', content)

        if mentioned_users:
            for username in mentioned_users:
                try:
                    # 查找提及的用户
                    receiver = User.objects.get(username=username).id
                    print(review.ownerNo_id)

                    # 创建 atMessage 数据
                    at_message = atMessage.objects.create(
                        rno_id=review.rno,
                        senderno_id=review.ownerNo_id,  # 回复者
                        receiverno_id=receiver,  # 被提及的用户
                        status=False  # 默认是未读状态
                    )
                except User.DoesNotExist:
                    continue  # 如果用户不存在，则跳过

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
            review.likeNum = review.likeNum - 1
            review.save()
            # ser = ReviewSerializer(review)
            existing_like.delete()
            return Response({"code": 200, "message": '取消点赞成功'})
        else:
            # 如果不存在，则创建新的点赞
            review.likeNum = review.likeNum + 1
            review.save()
            new_like = models.Like.objects.create(userNo=user, rno=review)
            return Response({"code": 200, "message": '点赞成功'})

class AtMessageView(APIView):
    def get(self,request):
        user_id, user_type = extract_user_info_from_auth(request)
        atMessages = atMessage.objects.filter(receiverno_id=user_id)
        ser = AtMessageSerializer(atMessages, many=True)

        return  Response({"code": 200, "data": ser.data})

    #这里是改变已读状态的接口，新建@在回复和发帖部分
    def post(self,request):
        receive_user_id, user_type = extract_user_info_from_auth(request)
        atMessageId = request.data.get('atMessageId')
        message = atMessage.objects.filter(pk=atMessageId).first()
        message.status = True
        message.save()

        return Response({"code": 200, "message": '消息已读'})