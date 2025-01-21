from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from employee.models import Hierarchy

import ProjectK.data


def Home(request):
    if request.user.is_authenticated:
        print('Home: User is LoggedIn')

        inferiors = Hierarchy.objects.filter(superiorID=request.user.id)

        if len(inferiors) > 0:
            hasInferiors = True
            print('User has Employees')
        else:
            hasInferiors = False
            print('User has NO Employees')

        ##employeeName = User.objects.get(id=employee.id).last_name
        ##superior = User.objects.get(id=employee.superiorID)

        return render(request, 'home.html', {'hasInferiors': hasInferiors, 'name': request.user.last_name, 'home': 'active'})
    else:
        print('Home: User isn\'\t LoggedIn. Redirecting...')
        return redirect('/login')


def Logg(request):
    logout(request)
    return redirect('/login')
