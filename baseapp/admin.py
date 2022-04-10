from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UserDetails)
admin.site.register(Posts)
admin.site.register(PostLikes)
admin.site.register(CommentLikes)
admin.site.register(Comments)
admin.site.register(PageFollowers)
admin.site.register(Pages)
admin.site.register(Friends)
