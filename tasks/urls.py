from django.urls import path
from .views import TaskMain, NewTask
from .actors import getActorsOfStructure
from .contract import getContractsOfStructure
from .task_management import task_delete, task_end, task_end_request, task_end_request_deny, task_edit, copy
from chat.views import chat


urlpatterns = [
    path('', TaskMain),
    path('delete/<int:taskID>/', task_delete),
    path('end/<int:taskID>/', task_end),
    path('end-request/<int:taskID>/', task_end_request),
    path('deny-request/<int:taskID>/', task_end_request_deny),
    path('edit/<int:taskID>/', task_edit),
    path('chat/<int:taskID>/', chat),
    path('copy/<int:taskID>/', copy),
    path('new/', NewTask),
    path('getActors/', getActorsOfStructure),
    path('getContracts/', getContractsOfStructure)

]
