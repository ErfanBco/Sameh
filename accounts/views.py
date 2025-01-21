import re

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages



def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'POST':
        formPOST = request.POST
        user = User.objects.get(id=request.user.id)

        oldPass = formPOST.get('oldPass')
        newPass = formPOST.get('newPass')
        repetition = formPOST.get('PassRepetition')

        oldPassCheck = user.check_password(oldPass)
        lenCheck = 8 <= len(newPass) <= 12
        mismatchCheck = repetition == newPass
        ChangeCheck = not newPass == oldPass

        if oldPassCheck and mismatchCheck and lenCheck and ChangeCheck:
            user.set_password(newPass)
            user.save()
            return redirect('/login')
        else:
            if not oldPassCheck:
                messages.error(request, '!رمزعبور قبلی نادرست است', 'danger')
            if len(newPass) < 8:
                messages.error(request, '!رمزعبور جدید کوتاه است', 'danger')
            if len(newPass) > 12:
                messages.error(request, '!رمزعبور جدید بلند است', 'danger')
            if not mismatchCheck:
                messages.error(request, '!رمزعبور جدید با تکرارش همخوانی ندارد', 'danger')
            if not ChangeCheck:
                messages.error(request, '!رمزعبور جدید با رمزعبور قبلی نمیتواند یکی باشد', 'danger')

    return render(request, 'changePassword.html')
