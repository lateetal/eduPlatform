from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import chatRoom
from chatRoom import models
from chatRoom.models import Discussion, Review, PictureReview, PictureDisscussion, Like, atMessage, FavoritesFolder, \
    Favorite, Topic, DiscussionWithTopic, Follow, FavoritesFolderOfOthers
from chatRoom.serializers import discussionSerializer, ReviewSerializer, AtMessageSerializer, FloderSerializer, \
    FloderDetailSerializer, FollowSerializer, ComprehensiveFloderSerializer, FanSerializer
from homepage.models import Course
from homepage.views import extract_user_info_from_auth
from login.models import User
from fuzzywuzzy import fuzz
import re


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

            combined_text = title + ' ' + info
            topics = re.findall(r'#(\w+)', combined_text)  # 提取所有 @后跟的用户名

            for topic_name in topics:
                topic, created = Topic.objects.get_or_create(tname=topic_name)
                DiscussionWithTopic.objects.create(dno_id=new_discussion.dno, tno_id=topic.tno)

            return Response({"code": 200, "data": ser.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self,request,course_id,dno):
        try:
            discussion = Discussion.objects.get(dno=dno)
            if discussion.havePic == 1:
                PictureDisscussion.objects.filter(dno=dno).delete()
            DiscussionWithTopic.objects.filter(dno_id=dno).delete()
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


class filterDiscussion(APIView):
    def post(self, request, course_id):
        try:
            keyword = request.data.get('keyword').strip()
            if not keyword:
                return Response({"code": 400, "message": "请输入关键词"}, status=status.HTTP_400_BAD_REQUEST)

            user_id, user_type = extract_user_info_from_auth(request)

            # 根据课程ID获取对应的讨论
            discussions = Discussion.objects.filter(cno_id=course_id)

            # 用来存储匹配的讨论
            matched_discussions = []

            # 用 fuzzywuzzy 比较每个讨论的标题和正文
            for discussion in discussions:
                title_score = fuzz.token_sort_ratio(discussion.dtitle, keyword)
                info_score = fuzz.token_sort_ratio(discussion.dinfo, keyword)

                # 如果标题或正文和关键词的相似度大于70就认为是匹配的
                if title_score > 40 or info_score > 40:
                    matched_discussions.append(discussion)

            # 序列化匹配到的讨论
            ser = discussionSerializer(matched_discussions, context={'user_id': user_id}, many=True)
            return Response({"code": 200, "data": ser.data})

        except Discussion.DoesNotExist:
            return Response({'error': '讨论未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class showReview(APIView):
    def get(self, request,course_id,dno):
        try:
            user_id, user_type = extract_user_info_from_auth(request)
            discussion = Discussion.objects.get(dno=dno)
            reviews = Review.objects.filter(dno_id=dno)
            disSer = discussionSerializer(discussion, context={'user_id':user_id}, many=False)
            disData = disSer.data
            disData['reviews'] = ReviewSerializer(reviews, context={'user_id':user_id},many = True).data

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

                    # 解析 @用户名
            mentions = re.findall(r'@(\w+)', info)  # 提取所有 @后跟的用户名
            mentioned_users = []

            for username in mentions:
                try:
                    userid = User.objects.get(username=username).id
                    mentioned_users.append(userid)
                except User.DoesNotExist:
                    continue  # 如果找不到用户，就跳过

            # 创建 @消息记录
            for mentioned_user in mentioned_users:
                at_message = atMessage.objects.create(
                    rno=new_review,
                    senderno_id=owner_id,
                    receiverno_id=mentioned_user,
                    sendTime=timezone.now(),
                    status=False  # 初始状态为未读
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

            atMessage.objects.filter(rno=rno).delete()
            return Response({"code": 200, "message": '回复已经成功删除'})

        except Discussion.DoesNotExist:
            return Response({'error': '讨论未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class filterReview(APIView):
    def post(self, request, course_id,dno):
        try:
            # 获取用户的搜索关键词
            keyword = request.data.get('keyword', '').strip()
            if not keyword:
                return Response({"code": 400, "message": "请输入关键词"}, status=status.HTTP_400_BAD_REQUEST)

            # 获取当前用户的信息
            user_id, user_type = extract_user_info_from_auth(request)

            # 根据dno获取Discussion对象
            discussion = Discussion.objects.get(dno=dno)

            # 根据dno过滤出对应的评论（Review）
            reviews = Review.objects.filter(dno_id=dno)

            # 用来存储匹配的评论
            matched_reviews = []

            # 用 fuzzywuzzy 比较每个评论的rinfo和关键词
            for review in reviews:
                # 计算 rinfo 与关键词的相似度
                rinfo_score = fuzz.token_sort_ratio(review.rinfo, keyword)

                # 如果 rinfo 与关键词的相似度大于 40 就认为是匹配的
                if rinfo_score > 40:
                    matched_reviews.append(review)

            # 序列化讨论信息
            disSer = discussionSerializer(discussion)
            disData = disSer.data

            # 将匹配的评论序列化
            disData['reviews'] = ReviewSerializer(matched_reviews, context={'user_id': user_id}, many=True).data

            return Response({"code": 200, "data": disData})

        except Discussion.DoesNotExist:
            return Response({'error': '讨论未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Review.DoesNotExist:
            return Response({'error': '评论未找到'}, status=status.HTTP_404_NOT_FOUND)
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

class DiscussionLikeView(APIView):
    def post(self, request,dno):
        # 提取用户信息
        user_id, user_type = extract_user_info_from_auth(request)
        # 尝试获取用户和评论
        try:
            user = User.objects.get(pk=user_id)
            discussion = chatRoom.models.Discussion.objects.get(dno=dno)
        except User.DoesNotExist:
            return Response({'error': '用户未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Review.DoesNotExist:
            return Response({'error': '回复未找到'}, status=status.HTTP_404_NOT_FOUND)

        # 检查用户是否已经点赞
        existing_like = chatRoom.models.DiscussionLike.objects.filter(userNo=user, dno=discussion).first()

        if existing_like:
            # 如果存在，则删除点赞
            discussion.like = discussion.like - 1
            discussion.save()
            # ser = ReviewSerializer(review)
            existing_like.delete()
            return Response({"code": 200, "message": '取消点赞成功'})
        else:
            # 如果不存在，则创建新的点赞
            discussion.like = discussion.like + 1
            discussion.save()
            new_like = models.DiscussionLike.objects.create(userNo=user, dno=discussion)
            return Response({"code": 200, "message": '点赞成功'})

#对收藏夹点赞的逻辑
class FavoritesFolderLike(APIView):
    def post(self, request):
        # 提取用户信息
        user_id, user_type = extract_user_info_from_auth(request)
        fno = request.data.get('fno')
        # 尝试获取用户和收藏夹
        try:
            user = User.objects.get(pk=user_id)
            folder = FavoritesFolder.objects.get(fno=fno)
        except User.DoesNotExist:
            return Response({'error': '用户未找到'}, status=status.HTTP_404_NOT_FOUND)
        except FavoritesFolder.DoesNotExist:
            return Response({'error': '收藏夹未找到'}, status=status.HTTP_404_NOT_FOUND)

        # 检查用户是否已经点赞该收藏夹
        existing_like = models.FavoritesFolderLike.objects.filter(userNo=user, fno=folder).first()

        if existing_like:
            # 如果存在，则删除点赞
            folder.likeNum = folder.likeNum - 1
            folder.save()
            existing_like.delete()
            return Response({"code": 200, "message": '取消点赞成功'})
        else:
            # 如果不存在，则创建新的点赞
            folder.likeNum = folder.likeNum + 1
            folder.save()
            new_like = models.FavoritesFolderLike.objects.create(userNo=user, fno=folder)
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
        atMessageId = request.data.get('messageId')
        message = atMessage.objects.filter(pk=atMessageId).first()
        message.status = True
        message.save()

        return Response({"code": 200, "message": '消息已读'})

#用户看他人也通过这个接口来找，根据status来决定展示与否
class FavoriteFolder(APIView):
    def get(self,request):
        user_id, user_type = extract_user_info_from_auth(request)

        # 获取当前用户的个人收藏夹
        personal_folders = FavoritesFolder.objects.filter(userNo_id=user_id)

        # 获取他人的收藏夹
        others_folders = FavoritesFolderOfOthers.objects.filter(collector_id=user_id)

        # 创建序列化器实例，传递查询集和上下文
        ser = ComprehensiveFloderSerializer(
            instance={'personal_folders': personal_folders, 'others_folders': others_folders},
            context={'user_id': user_id}
        )
        return Response({"code": 200, "data": ser.data})

    def post(self,request):
        user_id, user_type = extract_user_info_from_auth(request)
        fname = request.data.get('fname')
        fstatus = request.data.get('fstatus')#可能前端应该是一个按钮

        models.FavoritesFolder.objects.create(userNo_id=user_id, fname=fname, fstatus=fstatus)

        return Response({"code": 200, "message": "收藏夹创建成功"})

    def delete(self,request):
        user_id, user_type = extract_user_info_from_auth(request)
        fname = request.data.get('fname')

        models.FavoritesFolder.objects.filter(userNo_id=user_id, fname=fname).delete()
        return Response({"code": 200, "data": fname})

    def put(self,request):
        user_id, user_type = extract_user_info_from_auth(request)
        fno = request.data.get('fno')
        fstatus = request.data.get('fstatus')
        fname = request.data.get('fname')

        folder = FavoritesFolder.objects.get(pk=fno)
        folder.fstatus = fstatus
        folder.fname = fname
        folder.save()

        return Response({"code": 200, "message": "收藏夹修改成功"})

class FavoriteFolderDetail(APIView):
    def get(self,request,fno):
        user_id, user_type = extract_user_info_from_auth(request)
        folder = FavoritesFolder.objects.get(pk=fno)
        ser = FloderDetailSerializer(folder,many=False)

        return Response({"code": 200, "data": ser.data})

    def post(self, request, fno):
        user_id, user_type = extract_user_info_from_auth(request)
        dno = request.data.get('dno')

        # 检查是否已经存在相同的收藏记录
        existing_favorite = models.Favorite.objects.filter(fno_id=fno, dno_id=dno).first()

        if existing_favorite:
            return Response({"code": 400, "message": "该帖子已被收藏过了"})

        # 如果没有存在相同记录，则创建新的收藏记录
        models.Favorite.objects.create(fno_id=fno, dno_id=dno)
        return Response({"code": 200, "message": "帖子收藏成功"})

    def delete(self,request,fno):
        user_id, user_type = extract_user_info_from_auth(request)
        dno = request.data.get('dno')
        Favorite.objects.get(fno_id=fno,dno_id=dno).delete()

        return  Response({"code": 200, "message": "帖子收藏删除成功"})

    def put(self,request,fno):
        user_id, user_type = extract_user_info_from_auth(request)
        dno = request.data.get('dno')
        newFno = request.data.get('newFno')

        favor = Favorite.objects.get(dno_id=dno,fno=fno)
        favor.fno_id = newFno
        favor.save()

        return Response({"code": 200, "message": "帖子收藏移动成功"})



#他人收藏夹部分
class otherfolder(APIView):
    def post(self, request):
        # 1. 从请求中提取用户信息
        user_id, user_type = extract_user_info_from_auth(request)

        # 2. 获取前端传来的fno（收藏夹序号）
        fno = request.data.get('fno')

        if not fno:
            return Response({"error": "没有fno"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. 查询收藏夹
            others_folder = FavoritesFolder.objects.get(fno=fno)
            if others_folder.userNo_id == user_id:
                return Response({"error": "不能收藏本人收藏夹"}, status=status.HTTP_404_NOT_FOUND)

        except FavoritesFolder.DoesNotExist:
            return Response({"error": "未找到该收藏夹"}, status=status.HTTP_404_NOT_FOUND)

        # 4. 创建FavoritesFolderOfOthers记录

        try:
            # 检查是否已经存在相同的记录
            if FavoritesFolderOfOthers.objects.filter(fno=others_folder, collector_id=user_id).exists():
                return Response({"message": "该收藏夹已经被收藏过了"}, status=status.HTTP_400_BAD_REQUEST)

            # 如果不存在，创建新的收藏夹记录
            new_favorites_folder_of_others = FavoritesFolderOfOthers(
                fno=others_folder,
                collector_id=user_id
            )
            new_favorites_folder_of_others.save()

            return Response({"message": "已经成功收藏别人的收藏夹"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        # 1. 从请求中提取用户信息
        user_id, user_type = extract_user_info_from_auth(request)

        # 2. 获取前端传来的fno（收藏夹序号）
        fno = request.data.get('fno')

        if not fno:
            return Response({"error": "没有fno"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. 查询收藏夹
            others_folder = FavoritesFolder.objects.get(fno=fno)
        except FavoritesFolder.DoesNotExist:
            return Response({"error": "未找到该收藏夹"}, status=status.HTTP_404_NOT_FOUND)

            # 4. 查找并删除对应的收藏记录
        favorite_record = FavoritesFolderOfOthers.objects.get(fno=others_folder, collector=user_id)
        favorite_record.delete()

        return Response({"message": "已取消收藏该收藏夹"}, status=status.HTTP_200_OK)


#展示对应话题下的讨论
class showTopic(APIView):
    def get(self, request, course_id):
        topic_name = request.data.get('topic')  # 获取请求中的话题
        try:
            course = Course.objects.get(cno=course_id)  # 假设你有 Course 模型，并且 course_id 对应 cno
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            topic = Topic.objects.get(tname=topic_name)
        except Topic.DoesNotExist:
            return Response({'error': 'Topic not found'}, status=status.HTTP_404_NOT_FOUND)

        discussion_ids = DiscussionWithTopic.objects.filter(tno=topic).values_list('dno', flat=True)
        discussions = Discussion.objects.filter(cno=course, dno__in=discussion_ids)
        ser = discussionSerializer(discussions, context={'user_id': request.user.id}, many=True)
        return Response(ser.data)

#救我我要被绕晕了
#获取用户的关注者
class followerView(APIView):
    def get(self,request):#获取关注列表
        user_id, user_type = extract_user_info_from_auth(request)
        followed = Follow.objects.filter(fan_id=user_id)
        ser = FollowSerializer(followed,many=True)

        return Response({"code": 200, "data": ser.data})

    def post(self,request):#新加关注
        user_id, user_type = extract_user_info_from_auth(request)
        follower = request.data.get('follower')
        follower_id = User.objects.get(username=follower).id
        Follow.objects.create(followed_id=follower_id, fan_id=user_id)

        return Response({"code": 200, "message":"关注成功"})
    def delete(self,request):
        user_id, user_type = extract_user_info_from_auth(request)
        follower = request.data.get('follower')
        follower_id = User.objects.get(username=follower).id
        Follow.objects.get(followed_id=follower_id, fan_id=user_id).delete()

        return Response({"code": 200, "message":"取关成功"})

#获取用户粉丝
class fanView(APIView):
    def get(self,request):
        user_id, user_type = extract_user_info_from_auth(request)
        fan = Follow.objects.filter(followed_id=user_id)
        ser = FanSerializer(fan,many=True)
        return Response({"code": 200, "data": ser.data})

    def delete(self,request):
        user_id, user_type = extract_user_info_from_auth(request)
        fan = request.data.get('fan')
        fan_id = User.objects.get(username=fan).id
        Follow.objects.get(followed_id=user_id, fan_id=fan_id).delete()

        return Response({"code": 200, "message":"移除粉丝成功"})


