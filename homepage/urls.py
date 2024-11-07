from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from homepage import views

urlpatterns = [
    path('student/',views.StudentHomePageView.as_view(),name='studenthomepage'),
    path('teacher/',views.TeacherHomePageView.as_view(),name='teacherhomepage'),
    path('getusername/',views.GetUsername.as_view(),name='getusername'),
    path('course/<str:course_id>/', views.GetCourseDetails.as_view(), name='course-detail'),
    path('course/<str:course_no>/update_intro', views.UpdateCourseIntro.as_view(), name='update_course_intro'),

    path('aichat',views.AIchat.as_view(),name='aichat'),
    path('course/<str:course_id>/message',views.CourseMessagesView.as_view(),name='messagesView'),
    path('course/message',views.AllCourseMessage.as_view(),name='messagesView'),
    path('course/<str:course_id>/student',views.AllStudent.as_view(),name='studentView'),

]
