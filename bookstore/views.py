from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# Public Home Page
def home(request):
    return render(request, 'home.html')


# Authentication -----------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    error = ''
    if request.method == 'POST':
        username = request.POST['user']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            error = "Passwords do not match!"
        elif User.objects.filter(username=username).exists():
            error = "Username already taken!"
        elif User.objects.filter(email=email).exists():
            error = "Email already registered!"
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            return redirect("dashboard")

    context = { "error": error }
    return render(request, 'auth/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    error = ''
    if request.method == 'POST':
        username = request.POST['user']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Invalid Credentials"
    
    context = { "error": error }
    return render(request, 'auth/login.html', context)


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')  # Create this template
# Authentication -----------------