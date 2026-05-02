from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        return render(request, 'accounts/login.html', {'error': '用户名或密码错误'})
    return render(request, 'accounts/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not username or not password:
            return render(request, 'accounts/register.html', {'error': '请填写完整信息'})
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': '用户名已存在'})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('index')
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')
