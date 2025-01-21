from django.contrib import admin
from .models import Chat


@admin.register(Chat)
class LeniencyAdmin(admin.ModelAdmin):
    list_display = ("message", 'sender', 'sender_name', 'taskID', 'send_date', 'seenBySuperior', 'seenByInDirectSuperior', 'seenByEmployee')
