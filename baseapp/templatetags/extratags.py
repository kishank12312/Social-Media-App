import imp
from urllib import request
from django import template
from ..models import *
register = template.Library()

@register.filter
def profilepicfromuser(user):
    userdetail = UserDetails.objects.get(user=user)
    return userdetail.ProfilePic.url

@register.filter
def liked(cwl):
    if cwl[1]:
        if cwl[1][0] == request.user:
            return True
        else: return False
    else:
        return False