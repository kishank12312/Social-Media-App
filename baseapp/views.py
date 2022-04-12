from ast import Lambda
import imp
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from .models import *
from .functions import *

cursor = connection.cursor()

# Create your views here.
def home(request):

    return render(request, 'baseapp/home.html')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('feed'))
            

    return render(request, 'baseapp/Login.html')

def signup(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'baseapp/SignUp.html', context)

def logoutPage(request):
    logout(request)
    return redirect(reverse('login'))

def feed(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    
    context = {}

    #POSTS
    final_posts = []
    final_posts_with_likes = []
    userFriends = findfriends(request.user)
    userPages = findFollowedPages(request.user)
    context['pagesFollowed'] = userPages
    for friend in userFriends:
        for post in findUserPosts(friend):
            final_posts.append(post)
    for page in userPages:
        for post in findPagePosts(page):
            final_posts.append(post)
    final_posts.sort(key=lambda x:x.PostedOn)
    for post in final_posts:
        if PostLikes.objects.filter(post=post,user=request.user).first():
            final_posts_with_likes.append((post,True))
        else:
            final_posts_with_likes.append((post,False))
    context['posts'] = final_posts_with_likes


    #FRIEND REQUESTS
    requestingUsers = friendRequests(request.user)
    context['friendRequests'] = requestingUsers


    

    return render(request, 'baseapp/Feed.html',context)

def posts(request,postID):
    context = []
    post = Posts.objects.get(PostID=postID)
    postedUserDetail = UserDetails.objects.get(user=post.user)

    #CHECKING PRIVACY
    if postedUserDetail.Private:
        if (not request.user.is_authenticated):
            return redirect(reverse('login'))
        elif (not checkFriends(post.user, request.user)):
            return redirect(reverse('feed'))
    

    comments = Comments.objects.filter(post=post)
    commentWithLikes = []
    for comment in comments:
        Likers = []
        for likeobjecct in CommentLikes.objects.filter(comment=comment):
            if likeobjecct.user == request.user:
                Likers = [likeobjecct.user] + Likers
            else:
                Likers.append(likeobjecct.user)
        commentWithLikes.append((comment,Likers))
    