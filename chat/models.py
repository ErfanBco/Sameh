from django.db import models


class Chat(models.Model):
    message = models.TextField()
    sender = models.IntegerField()
    sender_name = models.CharField(max_length=30)
    taskID = models.IntegerField()
    send_date = models.DateTimeField()
    seenBySuperior = models.BooleanField(default=False)
    seenByInDirectSuperior = models.BooleanField(default=False)
    seenByEmployee = models.BooleanField(default=False)
    seenByValidator = models.BooleanField(default=False)
    systemMessage = models.BooleanField(default=False)
