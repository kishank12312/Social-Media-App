from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.loginPage, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logoutPage, name='logout'),
    path('feed', views.feed, name='feed'),
    path('abcd', views.abcd),
    path('post/<int:postID>/', views.posts, name='post'),
]
