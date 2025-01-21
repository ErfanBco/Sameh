from django.contrib import admin
from .models import Hierarchy, Salary, Leniency, Structure, Contract


# Register your models here.


@admin.register(Leniency)
class LeniencyAdmin(admin.ModelAdmin):
    list_display = ("userID", 'leniencyTasks', 'leniencyExtraHour', 'realExtraHour', 'month')


@admin.register(Hierarchy)
class HierarchyAdmin(admin.ModelAdmin):
    list_display = ("userID", "userID2", 'superiorID', 'structure', 'canDefineTasks')


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'upLine')


@admin.register(Contract)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fee', 'employerStructure', 'employeesStructure', 'startDate', 'endDate', 'isValid')


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ("userID", 'max_Tasks', 'max_ExtraHour', 'hourly_rate', 'userType', 'date')
