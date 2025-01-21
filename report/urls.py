from django.contrib import admin
from django.urls import path, include

import report.views

urlpatterns = [
    path('', report.views.report),
    path('leniency/<int:userID>/', report.views.setLeniency),
    path('realExtraHour/<int:userID>/', report.views.setRealExtraHour)

]
