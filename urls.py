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
    path('course/<str:course_id>/resources/', views.CourseResourceListView.as_view(), name='course-resource-list'),
   # path('resource/<int:resource_id>/progress/', views.CourseResourceProgressView.as_view(), name='resource-progress'),
    
    path('course/<str:course_id>/assignments/', views.AssignmentListView.as_view(), name='assignment-list'),
    path('course/<str:course_id>/assignment/<int:assignment_id>/', views.AssignmentDetailView.as_view(), name='assignment-detail'),
    path('student/course/<str:course_id>/assignment/<int:assignment_id>/submit/', views.AssignmentSubmissionView.as_view(), name='assignment-submit'),
    path('upload/<str:course_id>/', views.UploadResourceView.as_view(), name='upload-resource'),
    path('course/<str:course_id>/create_assignment/', views.CreateAssignmentView.as_view(), name='create-assignment'),
]
