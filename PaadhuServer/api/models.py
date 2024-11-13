from django.db import models
from datetime import date

# Create your models here.

class UserModel(models.Model):
    userid = models.IntegerField()
    username = models.TextField(default="")
    emailid = models.TextField()
    mobileno = models.TextField()
    passwd = models.TextField()
    createddate = models.DateField(auto_now_add=True)
    rolename = models.TextField()
    userstatus = models.BooleanField(default="")
    domain = models.TextField()


class PatientModel(models.Model):
    patientid = models.IntegerField()
    demail = models.TextField()
    patientname = models.TextField()
    gender = models.TextField()
    weight = models.FloatField()
    age = models.IntegerField()
    createdtime = models.DateField()
    status = models.BooleanField()


class SessionModel(models.Model):
    sessionID = models.IntegerField()
    activityID = models.IntegerField()
    udevID = models.IntegerField()
    userID = models.IntegerField()
    sessionstatus = models.BooleanField()
    dataID = models.IntegerField()
    videoID = models.IntegerField()
    analystID = models.IntegerField()
    starttime = models.DateField()
    endtime = models.DateField

