from django.contrib import admin
from django.urls import path, include  # 包含 include 函数

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from login.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('homepage/', include('homepage.urls')),
    path('chatRoom/', include('chatRoom.urls')),

]
