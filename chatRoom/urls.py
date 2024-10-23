from django.contrib import admin
from django.urls import path
from chatRoom import views

urlpatterns = [

    path('<str:course_id>/discussion',views.showDiscussion.as_view(),name='discussionShow'),
    path('<str:course_id>/discussion/<str:dno>',views.showDiscussion.as_view(),name='discussionDelete'),
    path('<str:course_id>/discussion/<str:dno>/review',views.showReview.as_view(),name='discussionDelete'),

]
