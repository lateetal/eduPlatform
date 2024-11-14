from rest_framework import serializers

import chatRoom
from chatRoom.models import Discussion, Review, PictureDisscussion, PictureReview, Favorite, atMessage, FavoritesFolder, \
    DiscussionLike, Follow
from homepage.models import Student, Teacher
from login.models import User

#!!!!要解决的部分
#课程中讨论的展示
class discussionSerializer(serializers.ModelSerializer):
    pictures = serializers.SerializerMethodField()
    favor = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    ownerName = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = '__all__'
    def get_pictures(self, obj):
        if obj.havePic:
            pictures = PictureDisscussion.objects.filter(dno=obj)
            return PictureDisscussionSerializer(pictures,many=True).data
        return []

    def get_favor(self, obj):
        user_id = self.context.get('user_id')
        if user_id is not None:
            # 查找该用户所有收藏夹中的收藏记录
            folders = FavoritesFolder.objects.filter(userNo_id=user_id)
            favor_data = []  # 用于存储收藏夹信息的列表

            for folder in folders:
                # 判断当前讨论是否已被添加到该收藏夹中
                is_favored = Favorite.objects.filter(dno=obj, fno=folder).exists()

                # 将收藏夹的信息存入 favor_data 列表
                favor_data.append({
                    'fno': folder.fno,
                    'fname': folder.fname,
                    'is_favored': is_favored
                })

            return favor_data  # 返回收藏夹信息列表
        return []  # 如果没有找到用户 ID，返回空列表

    def get_ownerName(self, obj):
        user_id = obj.ownerNo_id
        if user_id is not None:
            username = User.objects.get(pk=user_id).username
            return username
        return False
    def get_is_liked(self, obj):
        user_id = self.context.get('user_id')
        dno = obj.dno
        try:
            # 尝试查询是否存在这个用户的点赞记录
            DiscussionLike.objects.get(userNo_id=user_id, dno=dno)
            return True  # 找到记录，则返回 True
        except DiscussionLike.DoesNotExist:
            # 如果找不到记录，则返回 False
            return False


#回帖详细信息
class ReviewSerializer(serializers.ModelSerializer):
    pictures = serializers.SerializerMethodField()
    discussion_is_liked = serializers.SerializerMethodField()
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
    def get_discussion_is_liked(self, obj):
        user_id = self.context.get('user_id')
        dno = obj.dno
        try:
            DiscussionLike.objects.get(userNo_id=user_id, dno=dno)
            return True  # 找到记录，则返回 True
        except DiscussionLike.DoesNotExist:
            return False


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

#无详细信息的收藏夹序列化
class FloderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoritesFolder
        fields = '__all__'

class FloderDetailSerializer(serializers.ModelSerializer):
    favorites = FavoriteSerializer(source='favorite_set', many=True)

    class Meta:
        model = FavoritesFolder
        fields = '__all__'
#属于FloderDetailSerializer进行嵌套序列化
class FavoriteSerializer(serializers.ModelSerializer):
    # 通过外键 dno 获取 Discussion 中的 dtitle 字段
    dtitle = serializers.CharField(source='dno.dtitle')

    class Meta:
         model = Favorite
         fields = ['fno', 'dtitle']

class FollowSerializer(serializers.ModelSerializer):
    fanUsername = serializers.SerializerMethodField()
    fanName = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['fan_id','fanName', 'fanUsername']

    def get_fanUsername(self, obj):
        fanUsername = User.objects.get(pk=obj.fan_id).username
        return fanUsername

    def get_fanName(self, obj):
        fanUserName = User.objects.get(pk=obj.fan_id).username
        fanType = User.objects.get(pk=obj.fan_id).user_type
        if fanType == 'student':
            return Student.objects.get(sno=fanUserName).sname
        else:
            return Teacher.objects.get(tno=fanUserName).tname