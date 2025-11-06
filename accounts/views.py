# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    print("METHOD:", request.method, "POST:", request.POST)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please enter both username and password")
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # ✅ only call login if user exists
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    else:
        # GET request -> just show the form
        return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)  # log the user out
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if not username or not password1 or not password2:
            messages.error(request, "Please fill out all fields")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(username=username, password=password1)
        user.save()

        # Automatically log the user in
        login(request, user)
        return redirect('workout_list')

    else:
        return render(request, 'accounts/signup.html')

