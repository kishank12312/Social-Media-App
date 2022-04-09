import imp
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

from django.contrib.auth import authenticate, login, logout

from .forms import CreateUserForm

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
    return render(request, 'baseapp/Feed.html')

