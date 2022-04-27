from django import template
from ..models import *
from ..functions import checkFriends
register = template.Library()

@register.filter
def profilepicfromuser(user):
    userdetail = UserDetails.objects.get(user=user)
    return userdetail.ProfilePic.url

@register.filter(takes_context=True)
def liked(cwl,user):
    if cwl[1]:
        if cwl[1][0] == user:
            return True
        else: return False
    else:
        return False

@register.filter(takes_context=True)
def likedpost(thispost,user):
    likers = PostLikes.objects.filter(post=thispost)
    for i in likers:
        if i.user == user:
            return True
    return False

@register.filter
def isNotFriendOf(user1,user2):
    print(user1,user2)
    return checkFriends(user1,user2)