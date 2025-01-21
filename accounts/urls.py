from django.urls import path, include
from accounts.views import changePassword



urlpatterns = [
    path('changePassword/', changePassword)

]