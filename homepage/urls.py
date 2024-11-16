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
    path('course/<str:course_id>/upload_file/<str:file_type>',views.uploadInfoFileView.as_view(),name='upload_file'),

    #lzy部分路径
    path('course/<str:course_id>/assignments/', views.AssignmentListView.as_view(), name='assignment-list'),
    path('course/<str:course_id>/assignment/<int:assignment_id>/', views.AssignmentDetailView.as_view(),
         name='assignment-detail'),
# 查看某个学生提交的作业详情
    path('course/<str:course_id>/assignment/<int:assignment_id>/student/<int:student_id>/', views.StudentSubmissionDetailView.as_view(),
         name='student-submission-detail'),
    path('student/course/<str:course_id>/assignment/<int:assignment_id>/submit/',views.AssignmentSubmissionView.as_view(), name='assignment-submit'),
    path('course/<str:course_id>/create_assignment/', views.CreateAssignmentView.as_view(), name='create-assignment'),

    #课程资源部分
    # path('course/<str:course_id>/resources_ppt/',views.CourseResourceListView_ppt.as_view(), name='resources_ppt'),
    path('course/<str:course_id>/resources_test/',views.CourseResourceListView_test.as_view(), name='resources_ppt'),
    path('course/<str:course_id>/resources_question/',views.CourseQuestionListView.as_view(), name='resources_question'),
    path('course/<str:course_id>/resources_question/<str:questionType>',views.CourseQuestionListView.as_view(), name='resources_question'),


]
