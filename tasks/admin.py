from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", 'title', 'comment', 'superior', 'employee', 'validator', 'fee', 'ValidatorFee', 'delay_punishment', 'final_payment', 'month', 'submit_date', 'delivery_date', 'finished_date', 'end_request_accepted', 'end_request_date', 'inProgress')
