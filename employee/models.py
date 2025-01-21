from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models





class Hierarchy(models.Model):
    #ToDo userID2 should replace userID
    userID = models.IntegerField(unique=False)
    userID2 = models.OneToOneField(User, unique=False, on_delete=models.PROTECT, blank=True, null=True)
    #TODO superior ID should be gone
    superiorID = models.IntegerField()
    structure = models.ForeignKey("Structure", unique=False, on_delete=models.PROTECT)
    #ToDo add Job Title If Necessary
    canDefineTasks = models.BooleanField()


class Contract(models.Model):
    name = models.CharField(max_length=40)
    fee = models.IntegerField()
    employerStructure = models.ForeignKey("Structure", unique=False, on_delete=models.PROTECT, related_name="asEmployer")
    employeesStructure = models.ForeignKey("Structure", unique=False, on_delete=models.PROTECT, related_name="asEmployee")
    startDate = models.DateField()
    endDate = models.DateField()
    isValid = models.BooleanField()



class Structure(models.Model):
    name = models.CharField(max_length=40)
    #UpLineID = models.IntegerField(unique=False)
    upLine = models.ForeignKey("Structure", unique=False, on_delete=models.PROTECT, related_name="DownLines", default=None, blank=True, null=True)


    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.upLine and self.upLine.name == self.name:
            raise ValidationError('You can\'t have The Structure as It\'s Own UpLine!')
        return super(Structure, self).save(*args, **kwargs)



class Salary(models.Model):
    userID = models.IntegerField()
    max_Tasks = models.IntegerField()
    max_ExtraHour = models.IntegerField()
    hourly_rate = models.IntegerField()
    #0 for Tagmii , 1 for barnameii
    userType = models.IntegerField()
    date = models.CharField(max_length=6)


class Leniency(models.Model):
    userID = models.IntegerField()
    leniencyTasks = models.IntegerField(default=0)
    leniencyExtraHour = models.IntegerField(default=0)
    realExtraHour = models.IntegerField(default=0)
    month = models.CharField(max_length=6)
