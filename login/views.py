from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from ProjectK.forms import LoginForm
from django.contrib import messages


def Login(request):
    if request.user.is_authenticated:
        return redirect('/tasks')
    if request.method == 'POST':
        print('Login: Checking Credentials...')
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            cleanedData = loginform.cleaned_data
            user = authenticate(request, username=cleanedData['username'], password=cleanedData['password'])
            if user is not None:
                login(request, user)
                print('Login: User '+user.username+' Logged In')
                return redirect('/tasks')

            else:
                print('Login: Wrong Credentials!')
                messages.error(request, '!نام کاربری یا رمزعبور وارد شده نادرست است', extra_tags='danger')
                return redirect('/login')
    else:
        print('Login: Showing Loging Form')
        loginform = LoginForm()
        return render(request, 'login.html', {'form': loginform})


