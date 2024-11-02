from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [

    # path('<str:course_id>/discussion',views.showDiscussion.as_view(),name='discussionShow'),
    path('/getinfo',views.HomeView.as_view(),name='home'),
    path('/updatePassword',views.Password.as_view(),name='updatePassword'),


]
