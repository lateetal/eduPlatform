from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status

# 自定义序列化器
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 添加用户类型到 token 中
        token['userType'] = user.user_type  # 假设 user_type 是你的用户模型中的字段
        return token

    def validate(self, attrs):
        # 在验证过程中，添加 userType
        data = super().validate(attrs)
        user = self.user  # 确保获取用户对象
        data['userType'] = user.user_type  # 将 userType 添加到返回数据中
        return data

# 自定义视图
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data  # 这里将获取到 userType
        return Response({
            'access': token['access'],
            'refresh': token['refresh'],
            'userType': token['userType'],  # 直接返回 userType
        }, status=status.HTTP_200_OK)