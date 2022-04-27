from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.loginPage, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logoutPage, name='logout'),
    path('feed', views.feed, name='feed'),
    path('abcd', views.abcd),
    path('friends', views.friends, name='friends'),
    path('post/<int:postID>/', views.posts, name='post'),
    path('user/<str:name>/',views.userpage,name='profile'),
    path('accountSetup',views.accountSetup,name='accountSetup'),
    path('edituser',views.editProfile,name='editProfile'),
    path('page/<int:id>',views.aboutPage,name='pages'),
    path('allPages',views.pagesPage,name='allPages')
]
