from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=50)
    comment = models.TextField(default=None, blank=True, null=True)
    superior = models.IntegerField()
    employee = models.IntegerField()
    validator = models.IntegerField()
    fee = models.IntegerField()
    ValidatorFee = models.IntegerField()
    delay_punishment = models.IntegerField()
    final_payment = models.IntegerField(default=0)
    ValidatorFinal_payment = models.IntegerField(default=0)
    month = models.CharField(max_length=6)
    submit_date = models.DateField()
    delivery_date = models.CharField(max_length=10)
    end_request_accepted = models.BooleanField(default=None, blank=True, null=True)
    end_request_date = models.DateTimeField(default=None, blank=True, null=True)
    finished_date = models.CharField(default=None, blank=True, null=True,max_length=10)
    inProgress = models.BooleanField(default=True)
