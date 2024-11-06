from django.contrib import admin
from django.urls import path
from chatRoom import views
import homepage

urlpatterns = [

    path('<str:course_id>/discussion',views.showDiscussion.as_view(),name='discussionShow'),
    path('<str:course_id>/discussion/<str:dno>',views.showDiscussion.as_view(),name='discussionDelete'),
    path('<str:course_id>/discussion/<str:dno>/review',views.showReview.as_view(),name='reviewShow'),
    path('<str:course_id>/discussion/<str:dno>/review/<str:rno>',views.showReview.as_view(),name='reviewDelete'),

    path('Like/<str:rno>', views.Like.as_view(), name='likeReview'),
    path('atmessage', views.AtMessageView.as_view(), name='atMessage'),

]
