from django.http import JsonResponse
from django.shortcuts import render, redirect

from .actors import ActorsObj
from .forms import CreateTaskForm
from django.db.models import Q
from employee.models import Hierarchy, Structure
from tasks.models import Task
from chat.models import Chat
from ProjectK.data import formatMonth, onlyFormatMonth, NumsToFa, isThereAnotherEndRequest, getDefaultMonth, \
    getTaskDelay
from django.contrib.auth.models import User
import datetime

from .structure import getEmployees, getAvailableStructures


def fixMonthFormatting(month):
    if len(str(month)) == 1:
        return '0' + str(month)
    else:
        return month


def NewTask(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    options = getEmployees(request.user.id)
    validators, _ = getValidators(request.user.id, None)
    createTaskForm = CreateTaskForm(args={'Options': options, 'Validators': validators, 'PreviousValues': None})

    return render(request, 'tasks/create/createForm2.html',
                  {'form': createTaskForm, 'StructuresJson': getAvailableStructures(request.user.id)})


def TaskMain(request):
    # ToDo Employees Filter should be default on All

    if not request.user.is_authenticated:
        return redirect('/login')
    options = getEmployees(request.user.id)
    validators, _ = getValidators(request.user.id, None)
    formPOST = request.POST

    if request.method == 'POST' and request.POST.get('title') is not None:
        print(formPOST.get('month'))
        for employee in formPOST.getlist('employee'):
            ValidatorIndex = formPOST.get('validator')
            Validator = parseValidator(ValidatorIndex, validators)

            Fee = int(formPOST.get('fee').replace(',', ''))
            ValidatorFee = int((formPOST.get('ValidatorFee') or '0').replace(',', ''))
            DelayPunishment = int(formPOST.get('delay_punishment').replace(',', ''))
            Month = formPOST.get('year') + (formPOST.get('month'))
            employeeID = User.objects.get(last_name=options[int(employee)][1]).id

            Task.objects.create(title=formPOST.get('title'), comment=formPOST.get('comment'),
                                submit_date=datetime.datetime.now(),
                                superior=request.user.id,
                                employee=employeeID,
                                validator=Validator,
                                fee=Fee,
                                ValidatorFee=ValidatorFee,
                                final_payment=0,
                                month=Month,
                                delay_punishment=DelayPunishment,
                                delivery_date=formPOST.get('delivery_date'))
        return redirect('/tasks/')
    else:
        formGET = request.GET
        createTaskForm = CreateTaskForm(args={'Options': options, 'Validators': validators, 'PreviousValues': None})
        # switch off means show inProgress Tasks
        # switch on means show finished Tasks
        try:
            cookie = str(request.COOKIES['switchStatus'])
        except:
            cookie = 'false'
        print(cookie)
        inProgress = formPOST.get('switch', cookie)
        print(inProgress)
        if inProgress == 'true':
            switchStatus = 'checked'
        else:
            switchStatus = 'unchecked'
        print(switchStatus)
        employeesRaw, employeesIDs, month, search, year = getFilters(formGET, options, request.user.id, True)
        DefinedTasks, TasksType, TasksCount2 = getTasks(request, inProgress, year + fixMonthFormatting(month), search,
                                                        employeesIDs)

        response = render(request, 'tasks/task.html',
                          {'form': createTaskForm, 'Tasks': DefinedTasks, 'TasksCount': len(DefinedTasks),
                           'TasksType': TasksType,
                           'index': 0, 'name': request.user.last_name, 'switchStatus': switchStatus,
                           'employees': options, 'employeesCount': len(options), 'employeesSelected': employeesRaw,
                           'search': search,
                           'current_month': onlyFormatMonth(fixMonthFormatting(month)),
                           'current_month_index': int(month), 'current_year': NumsToFa(year),
                           'current_year_index': int(year), 'ThisMonth': getDefaultMonth()[1],
                           'TasksCount2': TasksCount2})

        response.set_cookie('switchStatus', inProgress)
        return response


def getFilters(formGET, options, userID, addUserAtTheEnd):
    yearDefault, monthDefault = getDefaultMonth()
    searchDefault = ''

    month = formGET.get('month', monthDefault)
    year = formGET.get('year', yearDefault)
    search = formGET.get('search', searchDefault)
    employeesRaw = formGET.getlist('e')

    if int(month) > 12 or int(month) < 1:
        month = monthDefault
    if int(year) < 1300:
        year = yearDefault

    # TODO there is no filter to see YOUR tasks
    # print(employeesRaw)
    employeesIDs = []
    tmp = []
    optionsPlus = options
    if addUserAtTheEnd:
        optionsPlus.append((len(optionsPlus), User.objects.get(id=userID).last_name))
    for ID in employeesRaw:
        employeesIDs.append(User.objects.get(last_name=optionsPlus[int(ID)][1]).id)
        tmp.append(int(ID))
    employeesRaw = tmp
    return employeesRaw, employeesIDs, month, search, year


def getTasks(request, inProgress, TaskMonth, search, employeesIDs):
    # print('inProgress: ' + inProgress)
    InDirectSuperior = getInDirectSuperiorQ(request.user.id)
    if inProgress == 'false':
        EmployeeFilters = Q()  # Create an empty Q object to start with
        for ID in employeesIDs:
            EmployeeFilters |= (Q(employee=ID) | Q(validator=ID))
        DefinedTasks = Task.objects.filter(
            Q(employee=request.user.id) | Q(superior=request.user.id) | Q(validator=request.user.id) | InDirectSuperior) \
            .order_by('delivery_date').filter(inProgress=True).filter(month=TaskMonth).filter(title__contains=search) \
            .filter(EmployeeFilters)
    else:
        EmployeeFilters = Q()  # Create an empty Q object to start with
        for ID in employeesIDs:
            EmployeeFilters |= (Q(employee=ID) | Q(validator=ID))
        DefinedTasks = Task.objects.filter(
            Q(employee=request.user.id) | Q(superior=request.user.id) | Q(validator=request.user.id) | InDirectSuperior) \
            .order_by('delivery_date').filter(inProgress=False).filter(month=TaskMonth).filter(
            title__contains=search).filter(EmployeeFilters)

    TasksType = []
    TasksCount = [0, 0, 0, 0]
    print('User has ' + str(len(DefinedTasks)) + ' Tasks')
    for task in DefinedTasks:
        validator = User.objects.filter(id=task.validator)
        if validator.exists():
            validator = validator.first().last_name
        else:
            validator = None
        if task.employee == request.user.id:
            TasksType.append((task.id, 'Employee', User.objects.get(id=task.superior).last_name,
                              len(Chat.objects.filter(taskID=task.id).filter(~Q(sender=request.user.id)).filter(
                                  seenByEmployee=False)),
                              validator, task.inProgress, isThereAnotherEndRequest(task), getTaskDelay(task) > 0))
            TasksCount[0] += 1
        else:
            if task.superior == request.user.id:
                TasksType.append((task.id, 'Superior', User.objects.get(id=task.employee).last_name,
                                  len(Chat.objects.filter(taskID=task.id).filter(~Q(sender=request.user.id)).filter(
                                      seenBySuperior=False)),
                                  validator, task.inProgress, isThereAnotherEndRequest(task), getTaskDelay(task) > 0))
                TasksCount[1] += 1

            else:
                if task.validator == request.user.id:
                    TasksType.append((task.id, 'Validator', User.objects.get(id=task.employee).last_name,
                                      len(Chat.objects.filter(taskID=task.id).filter(~Q(sender=request.user.id)).filter(
                                          seenByValidator=False)), User.objects.get(id=task.superior).last_name,
                                      task.inProgress,
                                      isThereAnotherEndRequest(task), getTaskDelay(task) > 0))
                    TasksCount[2] += 1

                else:
                    TasksType.append((task.id, 'InDirectSuperior', User.objects.get(id=task.employee).last_name,
                                      len(Chat.objects.filter(taskID=task.id).filter(~Q(sender=request.user.id)).filter(
                                          seenByInDirectSuperior=False)), User.objects.get(id=task.superior).last_name,
                                      task.inProgress,
                                      isThereAnotherEndRequest(task), getTaskDelay(task) > 0))
                    TasksCount[3] += 1

        formatTask(task)
        # print(TasksType)
        # task.delivery_date = NumsToFa(JalaliDate[0])+'/'+NumsToFa(JalaliDate[1])+'/'+NumsToFa(JalaliDate[2])
    return DefinedTasks, TasksType, TasksCount


def getInDirectSuperiorQ(userID):
    InDirectSuperior = Q()
    for option in getEmployees(userID):
        InDirectSuperior |= Q(superior=User.objects.get(last_name=option[1]).id)
    return InDirectSuperior


def formatTask(task):
    task.fee = ('{:,}'.format(task.fee))
    task.final_payment = ('{:,}'.format(task.final_payment))
    task.ValidatorFee = ('{:,}'.format(task.ValidatorFee))
    task.ValidatorFinal_payment = ('{:,}'.format(task.ValidatorFinal_payment))
    task.delay_punishment = ('{:,}'.format(task.delay_punishment))
    task.month = formatMonth(task.month)


def getValidators(UserID, task):
    options = [(0, 'بدون تایید کننده')]
    PreviousValidator = 0
    Employees = Hierarchy.objects.filter(superiorID=UserID)
    i = 1
    for employee in Employees:
        options.append((i, User.objects.get(id=employee.userID).last_name))
        if task is not None and employee.userID == task.validator:
            PreviousValidator = i
        i += 1
    return options, PreviousValidator


def parseValidator(ValidatorIndex, validators):
    print(ValidatorIndex)
    if ValidatorIndex == '0':
        Validator = 0
    else:
        Validator = User.objects.get(last_name=validators[int(ValidatorIndex)][1]).id
    return Validator


#################################






