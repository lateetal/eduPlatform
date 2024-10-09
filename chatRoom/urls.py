from django.contrib import admin
from django.urls import path
from chatRoom import views

urlpatterns = [
    path('<str:course_id>/discussion',views.showDiscussion.as_view(),name='discussion'),
]
