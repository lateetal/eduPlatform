from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from homepage import views

urlpatterns = [
    path('student/',views.StudentHomePageView.as_view(),name='studenthomepage'),
    path('teacher/',views.TeacherHomePageView.as_view(),name='teacherhomepage'),
    path('getusername/',views.GetUsername.as_view(),name='getusername'),
    path('course/<str:course_id>/', views.GetCourseDetails.as_view(), name='course-detail'),
    path('course/<str:course_no>/update_intro/', views.update_course_intro, name='update_course_intro'),

    path('favorite', views.Favorites.as_view(), name='favoriteShow'),

    path('favorite/<str:dno>', views.Favorites.as_view(), name='favoriteUpdate'),

]
