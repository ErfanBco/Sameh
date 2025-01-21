import datetime
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Chat
from tasks.models import Task
from tasks.views import getInDirectSuperiorQ
from ProjectK.data import gregorian_to_jalali


def chat(request, taskID):
    if not request.user.is_authenticated:
        return redirect('/login')
    # Checking if user has access to this task

    InDirectSuperior = getInDirectSuperiorQ(request.user.id)
    current_task = Task.objects.filter(id=taskID).filter(
        Q(superior=request.user.id) | Q(employee=request.user.id) | Q(validator=request.user.id) | InDirectSuperior)
    if not (current_task.exists()):
        return redirect('/tasks')

    if request.method == 'POST':
        data = request.POST
        if not (data.get('message').strip() == ''):
            Chat.objects.create(taskID=taskID, sender=request.user.id, sender_name=request.user.last_name,
                                send_date=datetime.datetime.now().astimezone(), message=data.get('message').strip())

    Messages = getMessages(request.user.id, taskID)

    Contact = getContactName(current_task, request)

    title = current_task.first().title[0:30]
    if len(title) > 27:
        title = title[0:27] + '...'

    return render(request, 'chat.html',
                  {'Messages': Messages, 'MessagesCount': len(Messages), 'userID': request.user.id, 'Contact': Contact,
                   'TaskTitle': title, 'inProgress': current_task.first().inProgress})


def getMessages(UserID, taskID):
    Messages = Chat.objects.filter(taskID=taskID)
    task = Task.objects.get(id=taskID)
    if task.employee == UserID:
        Chat.objects.filter(taskID=taskID).filter(~Q(sender=UserID)).update(seenByEmployee=True)
    else:
        if task.superior == UserID:
            Chat.objects.filter(taskID=taskID).filter(~Q(sender=UserID)).update(seenBySuperior=True)
        else:
            Chat.objects.filter(taskID=taskID).filter(~Q(sender=UserID)).update(seenByInDirectSuperior=True)

    for Message in Messages:
        JalaliDate = gregorian_to_jalali(int(Message.send_date.strftime("%Y")), int(Message.send_date.strftime("%#m")),
                                         int(Message.send_date.strftime("%#d")))
        Message.send_date = JalaliDate[0] + '/' + JalaliDate[1] + '/' + JalaliDate[
            2] + '  ' + Message.send_date.astimezone().strftime('%H:%M')
    return Messages


def getContactName(current_task, request):
    if current_task.first().superior == request.user.id:
        Contact = User.objects.get(id=current_task.first().employee).last_name
    else:
        Contact = User.objects.get(id=current_task.first().superior).last_name
    return Contact
