from re import L
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from .models import *
from .functions import *
from django.db.models import Q
from .forms import CreateUserForm
from django.contrib import messages


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
        else:
            messages.info(request, 'Username or Password is incorrect.')

            

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
    
    myposts= Posts.objects.filter(user=request.user)
    for post in myposts:
        final_posts.append(post) 
    
    final_posts.sort(key=lambda x:x.PostedOn)
    final_posts.reverse()
    for post in final_posts:
        if PostLikes.objects.filter(post=post,user=request.user).first():
            final_posts_with_likes.append((post,True))
        else:
            final_posts_with_likes.append((post,False))
    context['posts'] = final_posts_with_likes

    #FRIEND REQUESTS
    requestingUsers = friendRequests(request.user)
    context['friendRequests'] = requestingUsers

    if request.method=="POST":
        newpost = Posts()
        newpost.user = request.user
        newpost.Title = request.POST.get('Title')
        newpost.Body = request.POST.get('Body') if 'Body' in request.POST else None
        newpost.LikeCount, newpost.CommentCount = 0,0
        pageval = request.POST.get('Page')
        if pageval == 'profile':
            newpost.page = None
        else:
            newpost.page = Pages.objects.get(PageID = int(pageval))
        newpost.Image = request.FILES['PostImage'] if 'PostImage' in request.FILES else None

        newpost.save()
        return redirect(reverse('feed'))


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
        elif request.GET.get('tag') == 'likepost':
            post_id = int(request.GET.get('id'))
            postobject = Posts.objects.get(PostID = post_id)
            newlike = PostLikes(post=postobject, user=request.user)
            newlike.save()
            postobject.LikeCount += 1
            postobject.save()
        elif request.GET.get('tag') == 'unlikepost':
            post_id = int(request.GET.get('id'))
            postobject = Posts.objects.get(PostID = post_id)
            existinglike = PostLikes.objects.get(post=postobject, user=request.user)
            existinglike.delete()
            postobject.LikeCount -= 1
            postobject.save()
            
            

    

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

    
    if request.method == 'POST':
        comment = request.POST.get('comment')
        newcomment = Comments(user=request.user, post=post)
        newcomment.Body = comment
        post.CommentCount += 1
        post.save()
        newcomment.save()

        return redirect(reverse('post', kwargs={'postID': post.PostID}))

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
        user=request.user, 
        Title='Why harry maguire could actually be the greatest defender of all time',
        Body="Harry Maguire has played in a World Cup semifinal and become one of the most highly rated defenders in the Premier League, but even his most ardent supporters would struggle to argue that he is the very best at his position.  Yet if Leicester get their way and force Manchester United to pay in excess of £80 million, the 26-year-old will become the most expensive defender in the world. That would eclipse the £75m that Liverpool paid for Virgil van Dijk -- not only the world's best defender but the favourite to win the Ballon d'Or this year.  All this for a player Leicester signed from relegated Hull City for an initial £12m just two years ago.",
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
            usermodel = User.objects.get(username=uname)
            frnd = Friends(Requester = request.user, Requested = usermodel, Confirmed = False)
            frnd.save()
        elif request.GET.get('tag') == 'friendrequest':
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
        elif request.GET.get('tag') == 'unfriend':
            print('something')
            uname = request.GET.get('userid')
            usermodel = User.objects.get(username=uname)
            frnd = Friends.objects.get(Requester=usermodel, Requested=request.user)
            frnd.delete()
 
    return render(request,'baseapp/Friends.html',context)



def userpage(request,name):
    context = {}
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    
    userPages = findFollowedPages(request.user)
    context['pagesFollowed'] = userPages
    accessuser = User.objects.get(username = name)
    context['accesseduser']=accessuser
    accessUserDetails = UserDetails.objects.get(user = accessuser)
    context['them']=accessUserDetails.Name
    if accessUserDetails.Private:
        if checkFriends(accessuser, request.user) |( accessuser == request.user):
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
            final_posts.reverse()

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
        final_posts.sort(key=lambda x:x.PostedOn, reverse=True)
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
        elif request.GET.get('tag') == 'likepost':
            post_id = int(request.GET.get('id'))
            postobject = Posts.objects.get(PostID = post_id)
            newlike = PostLikes(post=postobject, user=request.user)
            newlike.save()
            postobject.LikeCount += 1
            postobject.save()
        elif request.GET.get('tag') == 'unlikepost':
            post_id = int(request.GET.get('id'))
            postobject = Posts.objects.get(PostID = post_id)
            existinglike = PostLikes.objects.get(post=postobject, user=request.user)
            existinglike.delete()
            postobject.LikeCount -= 1
            postobject.save()

    return render(request,'baseapp/Profile.html',context)

def accountSetup(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
        
    context = {}
    if request.method == "POST":
        details = UserDetails()
        details.user = request.user
        details.Name = request.POST.get('Name')
        details.DateOfBirth = parsedDate(request.POST.get('DateOfBirth'))
        details.PhoneNumber = request.POST.get('PhoneNumber')
        details.Gender = request.POST.get('Gender')
        details.About = request.POST.get('About')
        details.Private = 'Private' in request.POST
        details.ProfilePic = request.FILES['ProfilePic']
 
        details.save()
 
        return redirect(reverse('feed'))
    return render(request,'baseapp/accountSetup.html',context)
    
def editProfile(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    
    context = {}
    if request.method == "POST":
        details = UserDetails.objects.get(user = request.user)
 
        details.Name = request.POST.get('Name')
        details.PhoneNumber = request.POST.get('PhoneNumber')
        details.Gender = request.POST.get('Gender')
        details.About = request.POST.get('About')
        details.Private = 'Private' in request.POST
        details.ProfilePic = request.FILES['ProfilePic']
 
        details.save()
 
        return redirect(reverse('feed'))
    return render(request,'baseapp/editUser.html',context)

def aboutPage(request,id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    
    context = {}
    
    currpage = Pages.objects.get(PageID=id)
    context['page']=currpage
    postsMade = Posts.objects.filter(page=currpage).order_by('PostedOn')
    final_posts = []
    final_posts_with_likes = []
    for post in postsMade:
        final_posts.append(post)
    final_posts.sort(key=lambda x:x.PostedOn)
    final_posts.reverse()
    for post in final_posts:
        if PostLikes.objects.filter(post=post,user=request.user).first():
            final_posts_with_likes.append((post,True))
        else:
            final_posts_with_likes.append((post,False))
    context['posts']=final_posts_with_likes
    pageFollows = PageFollowers.objects.filter(page=currpage)
    checker = [a.user for a in PageFollowers.objects.filter(page=currpage)]

    pageOwner = currpage.PageAdmin
    context['owner'] = pageOwner


    if (request.user not in checker) and request.user != pageOwner:
        context['allowfollow'] = True
    else:
        context['allowfollow'] = False
    context['followers'] = checker

    if request.method == 'GET':

        if request.GET.get('tag') == 'followpage':
            newflr = PageFollowers.objects.filter(page = currpage, user = request.user).exists()
            print(newflr)
            if newflr==False:
                newflr = PageFollowers(user = request.user, page = currpage)
                newflr.save()
        
        if request.GET.get('tag') == 'unfollowpage':
            PageFollowers.objects.filter(page = currpage, user = request.user).delete()

    return render(request,'baseapp/Pages.html',context)

def pagesPage(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    
    context = {}

    myPagesRaw = PageFollowers.objects.filter(user = request.user)
    pagesFollowed = [a.page for a in PageFollowers.objects.filter(user = request.user)]
    

    pagesCreated = [a for a in Pages.objects.filter(PageAdmin = request.user)]

    megaOthers = pagesFollowed + pagesCreated
    allOthers = [page for page in (Pages.objects.filter(~Q(PageID__in=[o.PageID for o in megaOthers])))]

    context['follow'] = pagesFollowed
    context['created'] = pagesCreated
    context['others'] = allOthers

    if request.method == 'GET':

        if request.GET.get('tag') == 'followpage':
            pid = request.GET.get('pageid')

            pagemodel = Pages.objects.get(PageID=pid)
            newflr = PageFollowers(user = request.user, page = pagemodel)
            newflr.save()

    if request.method=="POST":
        newpage = Pages()
        newpage.PageAdmin = request.user
        newpage.PageName = request.POST.get('PageName')
        newpage.About = request.POST.get('About') if 'About' in request.POST else None
        newpage.PageImage = request.FILES['PageImage'] if 'PageImage' in request.FILES else None

        newpage.save()
        pagefollower =  PageFollowers(page = newpage, user = request.user)
        pagefollower.save()

        return redirect(reverse('allPages'))


    return render(request, 'baseapp/allPages.html',context)


