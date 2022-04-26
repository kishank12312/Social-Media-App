from ast import Lambda
from contextlib import nullcontext
import imp
from turtle import pos
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from .models import *
from .functions import *
from django.db.models import Q
from .forms import CreateUserForm,AccountSetupForm


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


    if request.method == 'GET':
        if request.GET.get('tag') == 'friendrequest':
            req = request.GET.get('type')
            uname = request.GET.get('userid')
            print(uname,request)
            usermodel = User.objects.get(username=uname)
            if req == 'accept':
                frnd = Friends.objects.get(Requester=usermodel, Requested=request.user)
                frnd.Confirmed = True
                frnd.save()
            if req == 'reject':
                frnd = Friends.objects.get(Requester=usermodel, Requested=request.user)
                frnd.delete()
            
            

    

    return render(request, 'baseapp/Feed.html',context)

def posts(request,postID):
    context = {}
    post = Posts.objects.get(PostID=postID)
    #postedUserDetail = UserDetails.objects.get(user=post.user)

    #CHECKING PRIVACY
    # if postedUserDetail.Private:
    #     if (not request.user.is_authenticated):
    #         return redirect(reverse('login'))
    #     elif (not checkFriends(post.user, request.user)):
    #         return redirect(reverse('feed'))
    
    postlikeobjects = PostLikes.objects.filter(post=post)
    postLikers = [i.user for i in postlikeobjects]
    comments = Comments.objects.filter(post=post)
    commentWithLikes = []
    for comment in comments:
        Likers = []
        for likeobjecct in CommentLikes.objects.filter(comment=comment):
            if likeobjecct.user == request.user:
                Likers = [likeobjecct.user] + Likers
            else:
                Likers.append(likeobjecct.user)
        commentWithLikes.append((comment,Likers,len(Likers)))

    context['this_post']= post
    context['comment_info'] = commentWithLikes
    context['postLikers'] = postLikers

    if request.method == 'GET':
        if request.GET.get('tag') == 'likepost':
            post.LikeCount += 1
            post.save()
            newlike = PostLikes(post=post, user=request.user)
            newlike.save()
        elif request.GET.get('tag') == 'unlikepost':
            post.LikeCount -= 1
            post.save()
            likeobj = PostLikes.objects.get(post=post, user=request.user)
            likeobj.delete()
        elif request.GET.get('tag') == 'likecomment':
            cid = int(request.GET.get("cid"))
            cmnt = Comments.objects.get(CommentID = cid)
            newlike = CommentLikes(comment=cmnt, user=request.user)
            newlike.save()
        elif request.GET.get('tag') == 'unlikecomment':
            cid = int(request.GET.get("cid"))
            cmnt = Comments.objects.get(CommentID = cid)
            like = CommentLikes.objects.get(comment=cmnt, user=request.user)
            like.delete()

    return render(request,'baseapp/Post.html',context)
    

def abcd(request):
    p = Posts(
        user=User.objects.get(username='user1'), 
        Title='Proof that penandes is a fraud',
        Body="I was doing my LLM in Manchester and my professor told me that I couldn’t use a pencil, I had to use a pen. I checked my bag, and all my pens were gone. after looking at the security footage, I saw that PRUNO PENADES had taken all my pens! I was furious. Shame on you Penades",
        CommentCount=0,
        LikeCount=0,
        page=None
        )
    p.save()

    return HttpResponse("added")

def friends(request):
    context = {}
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    
    userFriends = findfriends(request.user)
    context['myFriends'] = userFriends
 
    requestingUsers = friendRequests(request.user)
    context['friendRequests'] = requestingUsers
    megaOthers = userFriends + requestingUsers
    megaOthers.append(request.user)
        
    allOthers = [user for user in (User.objects.filter(~Q(id__in=[o.id for o in megaOthers])))]
    
    requestedFellas = usersRequested(request.user)
    unrequisitedFellas = [el for el in allOthers if el not in requestedFellas]
    
    context['unknownPeople'] = unrequisitedFellas
    context['mySentPendingReqs'] = requestedFellas

    if request.method == 'GET':
        if request.GET.get('tag') == 'sendrequest':
            uname = request.GET.get('userid')
            print(uname,request)
            usermodel = User.objects.get(username=uname)
            frnd = Friends(Requester = request.user, Requested = usermodel, Confirmed = False)
            frnd.save()

 
    return render(request,'baseapp/Friends.html',context)



def userpage(request,name):
    context = {}
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    
    
    accessuser = User.objects.get(username = name)
    #context['them']=accessuser
    accessUserDetails = UserDetails.objects.get(user = accessuser)
    context['them']=accessUserDetails.Name
    if accessUserDetails.Private:
        if checkFriends(accessuser, request.user):
            #THEIR FRIENDS
            accessUserFriends = findfriends(accessuser)
            context['theirFriends'] = accessUserFriends

            #THEIR POSTS
            postsMade = Posts.objects.filter(user=accessuser,page=None).order_by('PostedOn')
            final_posts = []
            final_posts_with_likes = []
            for post in postsMade:
                final_posts.append(post)
            final_posts.sort(key=lambda x:x.PostedOn)
            for post in final_posts:
                if PostLikes.objects.filter(post=post,user=request.user).first():
                    final_posts_with_likes.append((post,True))
                else:
                    final_posts_with_likes.append((post,False))
            context['theirPosts'] = final_posts_with_likes 

            #ABOUT THEM
            context['theirInfo'] = accessUserDetails
        else:
            context['theirFriends']=None
            context['theirInfo']=accessUserDetails
            context['theirPosts']=None
    
    else:
        #THEIR FRIENDS
        accessUserFriends = findfriends(accessuser)
        context['theirFriends'] = accessUserFriends
        #THEIR POSTS
        postsMade = Posts.objects.filter(user=accessuser,page=None).order_by('PostedOn')
        final_posts = []
        final_posts_with_likes = []
        for post in postsMade:
            final_posts.append(post)
        final_posts.sort(key=lambda x:x.PostedOn)
        for post in final_posts:
            if PostLikes.objects.filter(post=post,user=request.user).first():
                final_posts_with_likes.append((post,True))
            else:
                final_posts_with_likes.append((post,False))
        context['theirPosts'] = final_posts_with_likes 

        #ABOUT THEM
        context['theirInfo'] = accessUserDetails


    if request.method == 'GET':
        if request.GET.get('tag') == 'sendrequest':
            frnd = Friends(Requester = request.user, Requested = accessuser, Confirmed = False)
            frnd.save()

    return render(request,'baseapp/Profile.html',context)

def accountSetup(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
        
    context = {}
    context['form'] = AccountSetupForm()
    if request.method == "POST":
        details = UserDetails()
        details.user = request.user
        details.Name = request.POST.get('Name')
        details.DateOfBirth = parsedDate(request.POST.get('DateOfBirth'))
        details.PhoneNumber = request.POST.get('PhoneNumber')
        details.About = request.POST.get('About')
        details.Private = 'Private' in request.POST
        details.ProfilePic = request.FILES['ProfilePic']
 
        details.save()
 
        return redirect(reverse('feed'))
    return render(request,'baseapp/accountSetup.html',context)
    
