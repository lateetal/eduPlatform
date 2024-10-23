from rest_framework import serializers

from chatRoom.models import Discussion, Review, PictureDisscussion, PictureReview


class discussionSerializer(serializers.ModelSerializer):
    pictures = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = '__all__'
    def get_pictures(self, obj):
        if obj.havePic:
            pictures = PictureDisscussion.objects.filter(dno=obj)
            return PictureDisscussionSerializer(pictures,many=True).data
        return []

class ReviewSerializer(serializers.ModelSerializer):
    pictures = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'
    def get_pictures(self, obj):
        if obj.havePic:
            pictures = PictureReview.objects.filter(rno=obj)
            return PictureDisscussionSerializer(pictures,many=True).data
        return []

class discussionDetailSerializer(discussionSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Discussion
        fields = '__all__'

class PictureDisscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureDisscussion
        fields = ['pfile']