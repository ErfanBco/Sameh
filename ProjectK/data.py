from datetime import datetime

from django.shortcuts import render, redirect

from home.models import Param


def isLoggedIn(request):
    if request.user.is_authenticated:
        print('Home: User is LoggedIn')
        return True
    else:
        print('Home: User isn\'\t LoggedIn. Redirecting...')
        return redirect('/login')


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gm > 2:
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)

    Year = str(jy)

    if len(str(jm)) == 1:
        Month = '0' + str(jm)
    else:
        Month = str(jm)

    if len(str(jd)) == 1:
        Day = '0' + str(jd)
    else:
        Day = str(jd)
    return [Year, Month, Day]


def jalali_to_gregorian(jy, jm, jd):
    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += ((days - 1) // 365)
        days = (days - 1) % 365
    gd = days + 1
    if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
        kab = 29
    else:
        kab = 28
    sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while gm < 13 and gd > sal_a[gm]:
        gd -= sal_a[gm]
        gm += 1

    Year = str(gy)

    if len(str(gm)) == 1:
        Month = '0' + str(gm)
    else:
        Month = str(gm)

    if len(str(gd)) == 1:
        Day = '0' + str(gd)
    else:
        Day = str(gd)
    return [Year, Month, gd]


def formatMonth(month):
    Y = month[0:4]
    M = month[4:6]
    switcher = {
        '01': "فروردین",
        '02': "اردیبهشت",
        '03': "خرداد",
        '04': "تیر",
        '05': "مرداد",
        '06': "شهریور",
        '07': "مهر",
        '08': "آبان",
        '09': "آذر",
        '10': "دی",
        '11': "بهمن",
        '12': "اسفند",
    }
    return switcher.get(M, "تعریف نشده") + ' ' + NumsToFa(Y)


def onlyFormatMonth(Month):
    switcher = {
        '01': "فروردین",
        '02': "اردیبهشت",
        '03': "خرداد",
        '04': "تیر",
        '05': "مرداد",
        '06': "شهریور",
        '07': "مهر",
        '08': "آبان",
        '09': "آذر",
        '10': "دی",
        '11': "بهمن",
        '12': "اسفند",
    }
    return switcher.get(Month, "تعریف نشده")


def NumsToFa(num):
    switcher = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹"
    }
    i = 0
    new_num = []
    while i < len(num):
        new_num.append(switcher.get(num[i], "0"))
        i += 1
    return ''.join(new_num)


def isThereAnotherEndRequest(task):
    if task.end_request_accepted is None and task.end_request_date is not None:
        return True
    else:
        return False


def getTodayJalaliDate():
    GregorianDate = [int(datetime.now().strftime("%Y")), int(datetime.now().strftime("%#m")),
                     int(datetime.now().strftime("%#d"))]
    return gregorian_to_jalali(GregorianDate[0], GregorianDate[1], GregorianDate[2])


def getDefaultMonth():
    Today = getTodayJalaliDate()
    month_deadline = int(Param.objects.get(key='month_deadline').value)
    if int(Today[2]) > month_deadline:
        Today[1] = str(int(Today[1]) + 1)
        if int(Today[1]) > 12:
            Today[0] = str(int(Today[0]) + 1)
            Today[1] = '1'

    print(Today[0]+'/'+Today[1])
    return Today[0], Today[1]


def getTaskDelay(task):
    DeliveryDateGregorian = task.delivery_date.split('/')
    Gregorian = jalali_to_gregorian(int(DeliveryDateGregorian[0]), int(DeliveryDateGregorian[1]),
                                    int(DeliveryDateGregorian[2]))
    delay = (datetime.now() - datetime.strptime(
        str(Gregorian[0]) + ' ' + str(Gregorian[1]) + ' ' + str(Gregorian[2]), '%Y %m %d')).days
    delay = max(delay, 0)
    return delay