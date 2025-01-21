import math
import sys

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect

from ProjectK.data import NumsToFa, onlyFormatMonth
from tasks.views import getFilters, fixMonthFormatting, formatTask
from tasks.structure import getEmployees
from tasks.models import Task
from employee.models import Salary, Leniency, Hierarchy


def report(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    options = getEmployees(request.user.id)

    month = getFilters(request.GET, options, request.user.id, False)[2]
    year = getFilters(request.GET, options, request.user.id, False)[4]
    options1D = options

    YearAltogetherPayment = 0
    YearAltogetherMonthlyBudget = 0
    AltogetherPayment = 0
    AltogetherMonthlyBudget = 0
    data2 = []
    MF = []

    employeesCount = len(options) + 1
    for BelowEmployee in options:
        options2D = [BelowEmployee]
        options2D = options2D + getEmployees(User.objects.get(last_name=BelowEmployee[1]).id)
        MF.append(options2D)

        yearAltogetherPayment, yearAltogetherMonthlyBudget, yearBudgetBalance, altogetherPayment, altogetherMonthlyBudget, budgetBalance, yearAltogetherPaymentBitch, yearAltogetherMonthlyBudgetBitch = getYearAltogetherInfo(
            options2D, year + fixMonthFormatting(month), len(options2D), request.user.id)

        print(str(User.objects.get(last_name=BelowEmployee[1]).id) + ';' + str(yearAltogetherPayment))
        YearAltogetherPayment += yearAltogetherPaymentBitch
        AltogetherPayment += altogetherPayment
        YearAltogetherMonthlyBudget += yearAltogetherMonthlyBudgetBitch
        AltogetherMonthlyBudget += altogetherMonthlyBudget

        if len(options2D) > 1:
            yearAltogetherPayment = ('{:,}'.format(int(yearAltogetherPayment)))
            altogetherPayment = ('{:,}'.format(int(altogetherPayment)))
            yearAltogetherMonthlyBudget = ('{:,}'.format(int(yearAltogetherMonthlyBudget)))
            altogetherMonthlyBudget = ('{:,}'.format(int(altogetherMonthlyBudget)))

            data2.append(
                (BelowEmployee[1], yearAltogetherPayment, yearAltogetherMonthlyBudget, yearBudgetBalance, altogetherPayment,
                 altogetherMonthlyBudget, budgetBalance))

        options = options + getEmployees(User.objects.get(last_name=BelowEmployee[1]).id)
    options.reverse()
    options.append((len(options), request.user.last_name))
    options.reverse()

    data, data3, AltogetherPayment, AltogetherMonthlyBudget, BudgetBalance, ignore, ignore2 = getTasks(options,
                                                                                                 year + fixMonthFormatting(
                                                                                                     month),
                                                                                                 employeesCount, request.user.id)

    YearBudgetBalance = YearAltogetherMonthlyBudget and round(
        ((YearAltogetherPayment / YearAltogetherMonthlyBudget) * 100)) or 0
    BudgetBalance = AltogetherMonthlyBudget and round(((AltogetherPayment / AltogetherMonthlyBudget) * 100)) or 0

    YearAltogetherPayment = ('{:,}'.format(int(YearAltogetherPayment)))
    AltogetherPayment = ('{:,}'.format(int(AltogetherPayment)))
    YearAltogetherMonthlyBudget = ('{:,}'.format(int(YearAltogetherMonthlyBudget)))
    AltogetherMonthlyBudget = ('{:,}'.format(int(AltogetherMonthlyBudget)))

    data2.append(('مجموع', YearAltogetherPayment, YearAltogetherMonthlyBudget, YearBudgetBalance, AltogetherPayment,
                  AltogetherMonthlyBudget, BudgetBalance))
    data2.reverse()

    return render(request, 'report/report.html', {'current_month_index': int(month), 'current_year_index': int(year),
                                                  'current_month': onlyFormatMonth(fixMonthFormatting(month)),
                                                  'current_year': NumsToFa(year),
                                                  'name': request.user.last_name, 'employees': options, 'Data': data,
                                                  'Data2': data2, 'Data3': data3, 'lenData3': len(data3), 'employeesCount': len(options), 'MF': MF
                                                  })


def getTasks(options, TaskMonth, employeesCount, userID):
    data = []
    data3 = []
    AltogetherPayment = 0
    AltogetherMonthlyBudget = 0
    AltogetherPaymentBitch = 0
    AltogetherMonthlyBudgetBitch = 0

    index = 0
    for employee in options:
        index += 1
        employeeID = User.objects.get(last_name=employee[1]).id
        if Hierarchy.objects.get(userID=employeeID).superiorID == 0:
            continue

        tasksAsEmployee = Task.objects.filter(employee=employeeID).filter(inProgress=False).filter(month=TaskMonth)
        tasksAsValidator = Task.objects.filter(validator=employeeID).filter(inProgress=False).filter(month=TaskMonth)
        AllTasks = Task.objects.filter(Q(employee=employeeID) | Q(validator=employeeID)).filter(month=TaskMonth)
        # print(str(employeeID) + ' Process Started')

        HourlyRate, maxTaskPayment, maxExtraHour, userType = getSalary(employeeID, TaskMonth)
        leniencyTasks, leniencyExtraHour, realExtraHour = getLeniency(employeeID, TaskMonth)

        TasksTotalPayment = 0
        TasksFee = 0
        TasksPaymentAsValidator = 0
        TasksAllFee = 0
        for task in tasksAsEmployee:
            TasksTotalPayment = TasksTotalPayment + task.final_payment
            TasksFee = TasksFee + task.fee
            if employeeID == userID:
                formatTask(task)
                data3.append(['اقدام', task.title, User.objects.get(id=task.superior).last_name, task.fee, task.final_payment, task.delivery_date, task.finished_date])

        for task in tasksAsValidator:
            TasksPaymentAsValidator += task.ValidatorFinal_payment

            if employeeID == userID:
                formatTask(task)
                data3.append(['تایید', task.title, User.objects.get(id=task.superior).last_name, task.ValidatorFee, task.ValidatorFinal_payment, task.delivery_date, task.finished_date])

        for task in AllTasks:
            if task.employee == employeeID:
                TasksAllFee += task.fee
            else:
                TasksAllFee += task.ValidatorFee

        TasksTotalPayment += TasksPaymentAsValidator

        # print(str(employeeID) + ' : ' + 'Raw Payment : ' + str(TasksTotalPayment))

        if employeesCount >= index:
            isYourEmployee = True
        else:
            isYourEmployee = False

        if userType == 1 and TasksFee < maxTaskPayment:
            ##user is 'Barnamei
            # print(str(employeeID) + ' : ' + ' is Barnamei.')
            # print(str(employeeID) + ' : ' + str(maxTaskPayment - TasksFee) + ' barnamei increase ')
            TasksTotalPayment = TasksTotalPayment + (maxTaskPayment - TasksFee)

        UnroundedTasksTotalPayment = TasksTotalPayment
        if TasksTotalPayment + ((leniencyTasks / 100) * maxTaskPayment) > maxTaskPayment:
            # print(str(employeeID) + ' : ' + 'Exceeded Max Task Payment!')
            # the AND and OR prevents Division by zero exception
            PerformanceExtraHour = HourlyRate and round(
                (TasksTotalPayment + ((leniencyTasks / 100) * maxTaskPayment) - min(maxTaskPayment + ((leniencyTasks / 100) * maxTaskPayment), maxTaskPayment)) / HourlyRate) or 0
            TasksTotalPercentage = 100
            TasksTotalPayment = maxTaskPayment + ((leniencyTasks / 100) * maxTaskPayment)
        else:
            TasksTotalPercentage = maxTaskPayment and round((TasksTotalPayment / maxTaskPayment) * 100) or 0
            TasksTotalPayment = ((leniencyTasks / 100) * maxTaskPayment) + ((TasksTotalPercentage/100) * maxTaskPayment)
            PerformanceExtraHour = 0

        ExtraWorkPayment = (PerformanceExtraHour + leniencyExtraHour) * HourlyRate

        maxTasksLeniency = 100 - TasksTotalPercentage
        MonthlyBudget = maxTaskPayment + (maxExtraHour * HourlyRate)
        YearlyBudget = getYearlyBudget(employeeID, TaskMonth)
        leniencyTotalPayment = ((leniencyTasks / 100) * maxTaskPayment) + (leniencyExtraHour * HourlyRate)
        leniencyYearTotalPayment = getYearTotalLeniency(employeeID, TaskMonth)
        TotalofTotal = (TasksTotalPayment + ExtraWorkPayment)
        UnroundedTasksTotalPayment += leniencyTotalPayment
        TotalExtraHour = int(leniencyExtraHour) + PerformanceExtraHour
        TasksTotalPercentage2 = TasksTotalPercentage + int(leniencyTasks)

        print(str(index))
        if index != 1:
            AltogetherPayment += TotalofTotal
            AltogetherMonthlyBudget += MonthlyBudget
        AltogetherPaymentBitch += TotalofTotal
        AltogetherMonthlyBudgetBitch += MonthlyBudget
        if TotalofTotal > MonthlyBudget:
            OverBudget = True
        else:
            OverBudget = False

        TotalofTotal = ('{:,}'.format(int(TotalofTotal)))
        TasksTotalPayment = ('{:,}'.format(int(TasksTotalPayment)))
        UnroundedTasksTotalPayment = ('{:,}'.format(int(UnroundedTasksTotalPayment)))
        TasksPaymentAsValidator = ('{:,}'.format(int(TasksPaymentAsValidator)))
        maxTaskPayment = ('{:,}'.format(maxTaskPayment))
        ExtraWorkPayment = ('{:,}'.format(ExtraWorkPayment))
        PerformanceExtraHour = ('{:,}'.format(PerformanceExtraHour))
        MonthlyBudget = ('{:,}'.format(MonthlyBudget))
        YearlyBudget = ('{:,}'.format(YearlyBudget))
        leniencyTotalPayment = ('{:,}'.format(int(leniencyTotalPayment)))
        leniencyYearTotalPayment = ('{:,}'.format(int(leniencyYearTotalPayment)))
        HourlyRate = ('{:,}'.format(int(HourlyRate)))
        TasksAllFee = ('{:,}'.format(int(TasksAllFee)))


        # print(str(employeeID) + ' : ' + 'TasksPayment:' + str(TasksTotalPayment))
        # print(str(employeeID) + ' : ' + 'TasksMaxPayment:' + str(maxTaskPayment))
        # print(str(employeeID) + ' : ' + 'PerformanceExtraHour:' + str(PerformanceExtraHour))
        # print(str(employeeID) + ' : ' + 'ExtraWorkPayment:' + str(ExtraWorkPayment))
        # print(str(employeeID) + ' : ' + 'HourlyRate:' + str(HourlyRate))
        # print(str(employeeID) + ' : ' + 'MonthlyBudget:' + str(MonthlyBudget))
        # print(str(employeeID) + ' : ' + 'Total of Total:' + str(TotalofTotal))

        data.append(
            [employee[1], len(tasksAsEmployee), TasksTotalPercentage, TasksTotalPayment, maxTaskPayment, leniencyTasks,
             leniencyExtraHour, PerformanceExtraHour, ExtraWorkPayment, TotalofTotal, employeeID, maxTasksLeniency,
             canLenient(employeeID), abs(int(leniencyTasks)), abs(int(leniencyExtraHour)), realExtraHour, MonthlyBudget,
             YearlyBudget, leniencyTotalPayment, leniencyYearTotalPayment, isYourEmployee, TasksPaymentAsValidator,
             HourlyRate, UnroundedTasksTotalPayment, TotalExtraHour, TasksTotalPercentage2, OverBudget, TasksAllFee, len(AllTasks)])

    BudgetBalance = AltogetherMonthlyBudget and round(((AltogetherPayment / AltogetherMonthlyBudget) * 100)) or 0
    # AltogetherPayment = ('{:,}'.format(int(AltogetherPayment)))
    # AltogetherMonthlyBudget = ('{:,}'.format(int(AltogetherMonthlyBudget)))
    return data, data3, AltogetherPayment, AltogetherMonthlyBudget, BudgetBalance, AltogetherPaymentBitch, AltogetherMonthlyBudgetBitch


def canLenient(userID):
    return not Task.objects.filter(inProgress=True).filter(employee=userID).exists()


def getYearAltogetherInfo(options, month, employeesCount, userID):
    Year = month[0:4]
    Month = month[4:6]
    YearAltogetherPayment = 0
    YearAltogetherPaymentBitch = 0
    AltogetherPayment = 0
    YearAltogetherMonthlyBudget = 0
    YearAltogetherMonthlyBudgetBitch = 0
    AltogetherMonthlyBudget = 0
    for i in range(1, int(Month) + 1):
        ThisMonth = str(Year) + str(fixMonthFormatting(i))
        tmp, tmp2, AltogetherPayment, AltogetherMonthlyBudget, BudgetBalance, AltogetherPaymentBitch, AltogetherMonthlyBudgetBitch = getTasks(
            options, ThisMonth, employeesCount, userID)
        YearAltogetherPayment += AltogetherPayment
        YearAltogetherMonthlyBudget += AltogetherMonthlyBudget

        YearAltogetherPaymentBitch += AltogetherPaymentBitch
        YearAltogetherMonthlyBudgetBitch += AltogetherMonthlyBudgetBitch

    YearBudgetBalance = YearAltogetherMonthlyBudget and round(
        ((YearAltogetherPayment / YearAltogetherMonthlyBudget) * 100)) or 0
    BudgetBalance = AltogetherMonthlyBudget and round(((AltogetherPayment / AltogetherMonthlyBudget) * 100)) or 0

    return YearAltogetherPayment, YearAltogetherMonthlyBudget, YearBudgetBalance, AltogetherPayment, AltogetherMonthlyBudget, BudgetBalance, YearAltogetherPaymentBitch, YearAltogetherMonthlyBudgetBitch


def getLeniency(userID, month):
    objs = Leniency.objects.filter(userID=userID).filter(month=month)
    if objs.exists():
        return getattr(objs.first(), 'leniencyTasks'), getattr(objs.first(), 'leniencyExtraHour'), getattr(objs.first(),
                                                                                                           'realExtraHour')
    else:
        return 0, 0, 0


def getYearTotalLeniency(userID, month):
    Year = month[0:4]
    Month = month[4:6]
    YearTotalLeniency = 0
    for i in range(1, int(Month) + 1):
        ThisMonth = str(Year) + str(fixMonthFormatting(i))
        leniencyTasks, leniencyExtraHour, realExtraHour = getLeniency(userID, ThisMonth)
        HourlyRate, maxTaskPayment, maxExtraHour, userType = getSalary(userID, ThisMonth)
        YearTotalLeniency += ((leniencyTasks / 100) * maxTaskPayment) + (leniencyExtraHour * HourlyRate)
    return YearTotalLeniency


def getSalary(employeeID, month):
    records = Salary.objects.filter(userID=employeeID).order_by('-date').all()

    i = 0
    while i < len(records):
        if i + 1 == len(records):
            break
        if month < getattr(records[i], 'date'):
            i += 1
            continue
        else:
            break

    return getattr(records[i], 'hourly_rate'), getattr(records[i], 'max_Tasks'), getattr(records[i], 'max_ExtraHour'), getattr(records[i], 'userType')


def getYearlyBudget(employeeID, month):
    Year = month[0:4]
    Month = month[4:6]
    YearlyBudget = 0
    for i in range(1, int(Month) + 1):
        ThisMonth = str(Year) + str(fixMonthFormatting(i))
        HourlyRate, maxTaskPayment, maxExtraHour, userType = getSalary(employeeID, ThisMonth)
        YearlyBudget += maxTaskPayment + (maxExtraHour * HourlyRate)
    return YearlyBudget


def setLeniency(request, userID):
    data = request.POST
    LeniencyExtraHour = data.get('leniencyExtraHour', 0)
    LeniencyTasksPercentage = data.get('leniencyTasks', 0)
    print(str(LeniencyTasksPercentage))
    month = str(data.get('year')) + fixMonthFormatting(data.get('month'))

    if Leniency.objects.filter(userID=userID).filter(month=month).exists():
        Leniency.objects.filter(userID=userID).filter(month=month).update(leniencyExtraHour=LeniencyExtraHour,
                                                                          leniencyTasks=LeniencyTasksPercentage)
    else:
        Leniency.objects.create(userID=userID, leniencyExtraHour=LeniencyExtraHour,
                                leniencyTasks=LeniencyTasksPercentage, month=month)
    return redirect('/report')


def setRealExtraHour(request, userID):
    data = request.POST
    Month = str(data.get('year')) + fixMonthFormatting(data.get('month'))
    RealExtraHour = data.get('RealExtraHour', 0)
    PerformanceExtraHour = data.get('PerformanceExtraHour', 0)

    PerformanceExtraHour = PerformanceExtraHour.replace(',', '')
    RealExtraHour = RealExtraHour.replace(',', '')

    LeniencyExists = Leniency.objects.filter(month=Month).filter(userID=userID).exists()

    if int(RealExtraHour) > int(PerformanceExtraHour):
        H = int(RealExtraHour) - int(PerformanceExtraHour)
    else:
        if LeniencyExists:
            H = Leniency.objects.filter(month=Month).filter(userID=userID).first().leniencyExtraHour or 0
        else:
            H = 0

    if LeniencyExists:
        Leniency.objects.filter(month=Month).filter(userID=userID).update(realExtraHour=RealExtraHour,
                                                                          leniencyExtraHour=H)
    else:
        Leniency.objects.create(userID=userID, realExtraHour=RealExtraHour, leniencyExtraHour=H,
                                month=Month)
    return redirect('/report')
