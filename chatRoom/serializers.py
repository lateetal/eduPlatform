from rest_framework import serializers

from chatRoom.models import Discussion


class discussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = '__all__'
