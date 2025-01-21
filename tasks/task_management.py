from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
import datetime

from chat.models import Chat
from employee.models import Leniency
from .views import formatTask
from ProjectK.data import NumsToFa, jalali_to_gregorian, gregorian_to_jalali, isThereAnotherEndRequest, getTodayJalaliDate, getTaskDelay
from tasks.forms import EditTaskForm
from tasks.models import Task
from tasks.views import getValidators, fixMonthFormatting, parseValidator
from .structure import getEmployees


def task_delete(request, taskID):
    if not request.user.is_authenticated:
        return redirect('/login')
    # Checking if The Task Exists
    task = Task.objects.filter(id=taskID)
    if not task.exists():
        return redirect('/tasks')
    # Checking if user has Permission to delete Task
    first = task.first()
    if first.superior == request.user.id:
        first.delete()
    return redirect('/tasks')


def task_end(request, taskID):
    #TODO don't show validators payment for task creator when there is no validator
    if not request.user.is_authenticated:
        return redirect('/login')

    task = Task.objects.get(id=taskID)
    today = getTodayJalaliDate()

    if Task.objects.get(id=taskID).superior == request.user.id or Task.objects.get(id=taskID).validator == request.user.id:
        if request.method == 'POST':
            form = request.POST
            validatorFinal_payment = str(form.get('ValidatorFinal_payment', task.ValidatorFee)).replace(',', '')
            Finished_date = task.finished_date or NumsToFa(today[0]) + '/' + NumsToFa(today[1]) + '/' + NumsToFa(today[2])
            Task.objects.filter(id=taskID).update(final_payment=form.get('final_payment').replace(',', ''), ValidatorFinal_payment=validatorFinal_payment, inProgress=False, finished_date=Finished_date)

            Chat.objects.create(taskID=taskID, sender=request.user.id, sender_name='پیام سیستم',
                                send_date=datetime.datetime.now().astimezone(), message='اقدامات این برنامه تایید شد.', systemMessage=True)

            deleteLeniencyIfNecessary(task.month, task.employee, request)
            deleteLeniencyIfNecessary(task.month, task.validator, request)

            return redirect('/tasks')

        else:
            delay = getTaskDelay(task)

            if task.final_payment == 0:
                FinalFee = int(task.fee) - (delay * int(task.delay_punishment))
            else:
                FinalFee = task.final_payment
            if task.ValidatorFinal_payment == 0:
                ValidatorFinalFee = task.ValidatorFee
            else:
                ValidatorFinalFee = task.ValidatorFinal_payment
            formatTask(task)

            if task.validator == 0:
                HasValidator = False
            else:
                HasValidator = True
                task.validator = User.objects.get(id=task.validator).last_name

            if task.superior == request.user.id:
                isSuperior = True
            else:
                isSuperior = False



            task.employee = User.objects.get(id=task.employee).last_name



            return render(request, 'tasks/end_task.html', {'Task': task, 'Delay': delay, 'FinalFee': FinalFee,
                                                           'HasValidator': HasValidator, 'isSuperior': isSuperior,
                                                           'ValidatorFinalFee': ValidatorFinalFee,
                                                           'Today': NumsToFa(today[0]) + '/' + NumsToFa(
                                                               today[1]) + '/' + NumsToFa(today[2])})
    return redirect('/tasks')





def deleteLeniencyIfNecessary(Month, UserID, request):
    query = Leniency.objects.filter(month=Month).filter(userID=UserID)
    if query.exists() and query.first().leniencyTasks != 0:
        messages.info(request, 'ارفاق این ماه برای ' + User.objects.get(id=UserID).last_name + ' حذف شد',
                      extra_tags='info')
        query.update(leniencyTasks=0)


def task_end_request(request, taskID):
    if not request.user.is_authenticated:
        return redirect('/login')
    # Checking if user has Permission to request end to Task
    if Task.objects.get(id=taskID).employee == request.user.id:
        task = Task.objects.filter(id=taskID)
        if isThereAnotherEndRequest(task.first()):
            ##user has an unreviewed request already
            messages.error(request, '! شما قبلا درخواست خاتمه را ثبت کردید', extra_tags='danger')
            return redirect('/tasks')
        difference = 4 * 60 * 60
        if task.first().end_request_date is None or ((datetime.datetime.now().astimezone() - task.first().end_request_date).seconds >= difference):
            task.update(end_request_date=datetime.datetime.now(), end_request_accepted=None)
            Chat.objects.create(taskID=taskID, sender=request.user.id, sender_name='پیام سیستم',
                                send_date=datetime.datetime.now().astimezone(), message="درخواست خاتمه این برنامه اقدام توسط "+"<strong>"+User.objects.get(id=request.user.id).last_name+"</strong>"+" ثبت شد.", systemMessage=True)
            messages.success(request, '. درخواست شما ثبت شد', extra_tags='success')
        else:
            TimeDelta = (datetime.datetime.now().astimezone() - task.first().end_request_date).seconds
            messages.error(request, '! برای ثبت درخواست جدید, از آخرین درخواست رد شده شما باید 4 ساعت گذشته باشد(' + LeftTime(TimeDelta, difference) + ')',
                           extra_tags='danger')
    return redirect('/tasks')


def LeftTime(TimeDelta, difference):
    TimeDelta = difference - TimeDelta
    Hours = 0
    Min = 0
    MoreThanAnHour = False
    while TimeDelta >= 60:
        Min += 1
        TimeDelta -= 60
    while Min >= 60:
        Hours += 1
        Min -= 60
        MoreThanAnHour = True
    if MoreThanAnHour:
        return NumsToFa(str(Hours)) + ' ساعت و ' + NumsToFa(str(Min)) + ' دقیقه باقی مانده'
    else:
        return NumsToFa(str(Min)) + ' دقیقه باقی مانده'


def task_end_request_deny(request, taskID):
    if not request.user.is_authenticated:
        return redirect('/login')
    # Checking if user has Permission to request end to Task
    if Task.objects.get(id=taskID).superior == request.user.id or Task.objects.get(id=taskID).validator == request.user.id:
        Task.objects.filter(id=taskID).update(end_request_date=datetime.datetime.now(), end_request_accepted=False)

        Chat.objects.create(taskID=taskID, sender=request.user.id, sender_name='پیام سیستم',
                            send_date=datetime.datetime.now().astimezone(), message='اقدامات این برنامه رد شد.', systemMessage=True)
    return redirect('/tasks')


def task_edit(request, taskID):
    if not request.user.is_authenticated:
        return redirect('/login')
    # Checking if user has Permission to edit Task
    # TODO no employee edit

    task = Task.objects.get(id=taskID)
    if task.superior == request.user.id:
        form = request.POST
        options = getEmployees(request.user.id)
        validators, PreviousValidator = getValidators(request.user.id, task)

        if form.get('title') is None:
            PreviousValues = [task.title, task.comment, task.fee, task.delay_punishment, task.month[0:4],
                              task.delivery_date, task.ValidatorFee]
            Month = task.month[4:6]
            if Month[0] == '0':
                Month = '0' + Month[1]

            editTaskForm = EditTaskForm(
                args={'Validators': validators, 'PreviousValues': PreviousValues})
            return render(request, 'tasks/edit_task_2.html', {'form': editTaskForm, 'Month': Month, 'PreviousValidator': PreviousValidator})
        else:
            Fee = int(form.get('fee').replace(',', ''))
            ValidatorFee = int(form.get('ValidatorFee', '0').replace(',', ''))
            DelayPunishment = int(form.get('delay_punishment').replace(',', ''))

            Task.objects.filter(id=taskID).update(title=form.get('title'), comment=form.get('comment'),
                                                  fee=Fee, ValidatorFee=ValidatorFee, validator=parseValidator(form.get('validator'), validators),
                                                  month=form.get('year') + (form.get('month')),
                                                  delay_punishment=DelayPunishment,
                                                  delivery_date=form.get('delivery_date'))
            return redirect('/tasks')
    else:
        return redirect('/tasks')


def copy(request, taskID):
    if not request.user.is_authenticated:
        return redirect('/login')
    # Checking if user has Permission to request end to Task
    if Task.objects.get(id=taskID).superior != request.user.id:
        return redirect('/tasks')
    task = Task.objects.get(id=taskID)
    year = task.month[0:4]
    month = task.month[4:6]
    print(year)
    print(month)
    if month == '12':
        year = str(int(year) + 1)
        month = '01'
    else:
        month = fixMonthFormatting(str(int(month) + 1))

    DeliveryDate = task.delivery_date.split('/')
    if int(DeliveryDate[1]) <= 6:
        if int(DeliveryDate[1]) == 6 and int(DeliveryDate[2]) == 31:
            addedDays = 30
        else:
            addedDays = 31
    else:
        if int(DeliveryDate[1]) == 11 and int(DeliveryDate[2]) == 30:
            addedDays = 29
        else:
            addedDays = 30

    DeliveryDate = jalali_to_gregorian(int(DeliveryDate[0]), int(DeliveryDate[1]),
                                       int(DeliveryDate[2]))
    DeliveryDate = datetime.datetime.strptime(str(DeliveryDate[0]) + ' ' + str(DeliveryDate[1]) + ' ' + str(DeliveryDate[2]), '%Y %m %d') + datetime.timedelta(days=addedDays)
    DeliveryDate = DeliveryDate.strftime('%Y %m %d').split(' ')
    DeliveryDate = gregorian_to_jalali(int(DeliveryDate[0]), int(DeliveryDate[1]),
                                       int(DeliveryDate[2]))
    DeliveryDate = NumsToFa(DeliveryDate[0]) + '/' + NumsToFa(DeliveryDate[1]) + '/' + NumsToFa(DeliveryDate[2])

    Task.objects.create(title=task.title, comment=task.comment,
                        submit_date=datetime.datetime.now(),
                        superior=task.superior,
                        employee=task.employee,
                        validator=task.validator,
                        fee=task.fee,
                        ValidatorFee=task.ValidatorFee,
                        final_payment=0,
                        month=year + month,
                        delay_punishment=task.delay_punishment,
                        delivery_date=DeliveryDate)
    messages.success(request, ' .برنامه اقدام با موفقیت در ماه بعد تکثیر شد', 'success')
    return redirect('/tasks')
