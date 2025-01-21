from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


UserAdmin.list_display = ('id', 'username', 'last_name', 'is_active', 'is_staff', 'is_superuser')
