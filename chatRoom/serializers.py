from rest_framework import serializers

import chatRoom
from chatRoom.models import Discussion, Review, PictureDisscussion, PictureReview, Favorite

#课程中讨论的展示
class discussionSerializer(serializers.ModelSerializer):
    pictures = serializers.SerializerMethodField()
    is_favourited = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = '__all__'
    def get_pictures(self, obj):
        if obj.havePic:
            pictures = PictureDisscussion.objects.filter(dno=obj)
            return PictureDisscussionSerializer(pictures,many=True).data
        return []

    def get_is_favourited(self, obj):
        user_id = self.context.get('user_id')
        if user_id is not None:
            return Favorite.objects.filter(dno=obj,userNo_id=user_id).exists()
        return False

#回帖详细信息
class ReviewSerializer(serializers.ModelSerializer):


    pictures = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'
    def get_pictures(self, obj):
        if obj.havePic:
            pictures = PictureReview.objects.filter(rno=obj)
            return PictureDisscussionSerializer(pictures,many=True).data
        return []
    def get_is_liked(self, obj):
        user_id = self.context.get('user_id')
        if user_id is not None:
            return chatRoom.models.Like.objects.filter(rno=obj,userNo_id=user_id).exists()
        return False

class discussionDetailSerializer(discussionSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Discussion
        fields = '__all__'

class PictureDisscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureDisscussion
        fields = ['pfile']

class FavoriteSerializer(serializers.ModelSerializer):
    dis_detail = serializers.SerializerMethodField()
    class Meta:
        model = Favorite
        fields = '__all__'
    def get_dis_detail(self, obj):
        discussion = obj.dno
        return discussionDetailSerializer(discussion).data

# 收藏夹就不用预览图片了，就展示标题和正文，打开详细信息就跳转到课程展示的那一段逻辑{
#     "code": 200,
#     "data": [
#         {
#             "id": 4,
#             "dis_detail": {
#                 "dno": 20,
#                 "pictures": [],
#                 "dtitle": "课程2测试",
#                 "dinfo": "！",
#                 "postTime": "2024-10-23T01:08:43",
#                 "updateTime": "2024-10-23T01:08:45",
#                 "havePic": false,
#                 "cno": "0002",
#                 "ownerNo": 3
#             },
#             "dno": 20,
#             "userNo": 2
#         }
#     ]
# }