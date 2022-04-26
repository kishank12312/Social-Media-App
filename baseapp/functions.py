from operator import truediv
from urllib.request import Request
from .models import *
import datetime
 
def findfriends(user):
    friends = []
 
    friendsList = Friends.objects.filter(Requester=user, Confirmed=True) | Friends.objects.filter(Requested=user, Confirmed=True)
    for frienditem in friendsList:
        if frienditem.Requester == user:
            friends.append(frienditem.Requested)
        else:
            friends.append(frienditem.Requester)
    return friends
 
def findFollowedPages(user):
    pages = []
 
    pageFollowerObjects = PageFollowers.objects.filter(user=user)
    for item in pageFollowerObjects:
        pages.append(item.page)
    
    return pages
 
def findUserPosts(user):
    return Posts.objects.filter(user=user,page=None).order_by('PostedOn')
 
def findPagePosts(page):
    return Posts.objects.filter(page=page).order_by('PostedOn')
 
def friendRequests(user):
    wannabeFriends = []
    friendsList = Friends.objects.filter(Requested=user, Confirmed=False)
    for frienditem in friendsList:
        wannabeFriends.append(frienditem.Requester)
    return wannabeFriends
 
def usersRequested(user):
    userWannabe = []
    listOfThem = Friends.objects.filter(Requester=user,Confirmed=False)
    for friendsItem in listOfThem:
        userWannabe.append(friendsItem.Requested)
    return userWannabe
 
def checkFriends(user1,user2):
    one = Friends.objects.filter(Requester=user1,Requested=user2,Confirmed=True).first()
    two = Friends.objects.filter(Requester=user2,Requested=user1,Confirmed=True).first()
    if one or two: return True
    else: return False
 
def parsedDate(stringdate):
    parts = stringdate.split('-')
    parts = [int(i) for i in parts]
    dateval = datetime.date(parts[0],parts[1],parts[2])
    return dateval