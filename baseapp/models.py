from tkinter import Image
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserDetails(models.Model):
    GENDERS = (
        ('Male','Male'),
        ('Female','Female'),
        ('Others','Others')
    )
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    Name = models.CharField(max_length=150,null=True,blank=True)
    DateOfBirth = models.DateField()
    PhoneNumber = models.CharField(max_length=10)
    About = models.CharField(max_length=10000,blank=True)
    Gender = models.CharField(max_length=100, choices=GENDERS)
    Private = models.BooleanField()
    ProfilePic = models.ImageField(null= True, blank=True)


class Pages(models.Model):
    PageID = models.AutoField(primary_key=True)
    PageName = models.CharField(max_length=150)
    PageAdmin = models.ForeignKey(User, on_delete=models.CASCADE)
    About = models.CharField(max_length=10000)
    PageImage = models.ImageField(null= True, blank=True)

class Posts(models.Model):
    PostID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Title = models.CharField(max_length=150)
    Body = models.CharField(max_length=1000, null=True)
    PostedOn = models.DateTimeField(auto_now_add=True, null=True)
    CommentCount = models.IntegerField(null=True)
    LikeCount = models.IntegerField(null=True)
    page = models.ForeignKey(Pages, null=True, on_delete=models.CASCADE)
    Image = models.ImageField(null= True, blank=True)

class Comments(models.Model):
    CommentID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    CommentedOn = models.DateTimeField(auto_now_add=True, null=True)
    Body = models.CharField(max_length=300)

class Friends(models.Model):
    Requester = models.ForeignKey(User,on_delete=models.CASCADE, related_name='Requester')
    Requested = models.ForeignKey(User,on_delete=models.CASCADE, related_name='Requested')
    Confirmed = models.BooleanField()

class CommentLikes(models.Model):
    comment = models.ForeignKey(Comments,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

class PostLikes(models.Model):
    post = models.ForeignKey(Posts,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

class PageFollowers(models.Model):
    page = models.ForeignKey(Pages,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

