from rest_framework import serializers

import chatRoom
from chatRoom.models import Discussion, Review, PictureDisscussion, PictureReview, Favorite, atMessage
from homepage.models import CourseMessage
from login.models import User


#课程中讨论的展示
class discussionSerializer(serializers.ModelSerializer):
    pictures = serializers.SerializerMethodField()
    is_favourited = serializers.SerializerMethodField()
    ownerName = serializers.SerializerMethodField()

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
    def get_ownerName(self, obj):
        user_id = obj.ownerNo_id
        if user_id is not None:
            username = User.objects.get(pk=user_id).username
            return username
        return False

#回帖详细信息
class ReviewSerializer(serializers.ModelSerializer):
    pictures = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

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
    def get_username(self, obj):
        user = User.objects.get(id=obj.ownerNo_id)
        return user.username


class discussionDetailSerializer(discussionSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    ownerName = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = '__all__'
    def get_ownerName(self, obj):
        user_id = obj.ownerNo_id
        if user_id is not None:
            username = User.objects.get(pk=user_id).username
            return username
        return False

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

class AtMessageSerializer(serializers.ModelSerializer):
    # 定义一个方法字段来动态获取 dno
    dno = serializers.SerializerMethodField()
    rinfo = serializers.SerializerMethodField()
    cno = serializers.SerializerMethodField()

    class Meta:
        model = atMessage
        fields = '__all__'

    def get_dno(self, obj):
        # 获取与 atMessage 实例关联的 rno 对应的 Review 实例
        try:
            review = Review.objects.get(rno=obj.rno_id)  # 通过 rno 查找 Review 实例
            return review.dno.dno  # 返回 dno 的值
        except Review.DoesNotExist:
            return None  # 如果没有找到对应的 Review 实例，返回 None
    def get_rinfo(self, obj):
        rinfo = Review.objects.get(rno=obj.rno_id).rinfo
        return rinfo
    def get_cno(self, obj):
        dno = Review.objects.get(rno=obj.rno_id).dno_id
        cno = Discussion.objects.get(dno=dno).cno_id
        return cno