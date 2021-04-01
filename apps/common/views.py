from django.shortcuts import render, redirect
from apps.common.forms import UserForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from time_table.views import VideoCamera

app_name = 'time_table'


def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('time_table:setting')
            else:
                print("유저없음")
                form = LoginForm()
                return render(request, "common/login.html", {'form': form})
    else:
        form = LoginForm()
        return render(request, "common/login.html", {'form': form})


def face_login(request):
    if request.method == "POST":
        cam = VideoCamera()
        cam.get_frame()
        if cam.face_names:
            if cam.face_names[0] == 'Unknown':
                print('등록되지 않은 얼굴입니다')
                return redirect('login')
            user = User.objects.get(id=int(cam.face_names[0]))
            if user is not None:
                login(request, user)
                return redirect('time_table:setting')
            else:
                print("유저없음")
                form = LoginForm()
                return render(request, "common/login.html", {'form': form})
        else:
            return redirect('login')
    else:
        return redirect('login')


def update_profile(request):
    """
    계정생성
    """
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('time_table:setting')
    else:
        form = UserForm()
    return render(request, 'common/register.html', {'form': form})

