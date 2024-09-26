from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    userType = serializers.CharField(source='user_type')  # 假设有一个 user_type 字段

    class Meta:
        model = User
        fields = ['username', 'user_type', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
