from django.db import models
from django.conf import settings
from .validators import validate_Hostel_field
from django.core.validators import RegexValidator
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone


class Hostel_info(models.Model):
    user_ins = models.ForeignKey(settings.AUTH_USER_MODEL, default=1,
                                 blank=True, on_delete=models.CASCADE)
    Hostel_name = models.CharField(max_length=100)
    Hostel_Address = models.CharField(max_length=50)
    Hostel_Ph_No = models.PositiveIntegerField(
        null=True,blank=True)
    Hostel_Mobile_No = models.CharField(max_length=10,
       null=True, blank=True)
    Hostel_Price = models.PositiveIntegerField(blank=True,null=True)
    Hostel_Estd = models.DateTimeField('Date ESTD',default=timezone.now,null=True,blank=True)
    # Hostel_About = models.TextField(max_length=500,blank=True)
    Hostel_lat = models.CharField(max_length=250,blank=True,null=True)
    Hostel_long = models.CharField(max_length=250,blank=True,null=True)
    Hostel_type = models.CharField(max_length=250,blank=True,null=True,)
    wifi=models.BooleanField(default=False)
    lodging=models.BooleanField(default=False)
    studyRoom=models.BooleanField(default=False)
    laundary=models.BooleanField(default=False)
    medicalFacility=models.BooleanField(default=False)
    singleRoom=models.BooleanField(default=False)
    dormitory=models.BooleanField(default=False)
    about=models.TextField(max_length=200,blank=True)
    def image(self):
        return self.image_set.filter(Hostel_image=self.pk)

    def __str__(self):
        return self.Hostel_name

class Image(models.Model):
    Hostel_image = models.ForeignKey(Hostel_info, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='image/', blank=True)
    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)
    

class Hostel_comment(models.Model):
    comment = models.TextField(max_length=500, blank=True)
    commenton = models.ForeignKey(Hostel_info, on_delete=models.CASCADE)
    postdate=models.DateTimeField(auto_now_add=True)
   #user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, unique=False)
    timestamp=models.DateTimeField(auto_now_add=True)

class Hostel_Request(models.Model):
    user_ins = models.ForeignKey(settings.AUTH_USER_MODEL, default=1,
                                 blank=True, on_delete=models.SET_DEFAULT)
    Hostel_name = models.CharField(max_length=100)
    Hostel_Address = models.CharField(max_length=50)
    Hostel_Ph_No = models.PositiveIntegerField(
        null=True,blank=True,default=0)
    Hostel_Mobile_No = models.CharField(max_length=10,
        null=True,blank=True,default=0)
    Hostel_Price = models.PositiveIntegerField(default=0,null=True,blank=True,)
    Hostel_Estd = models.DateTimeField('Date ESTD',default=timezone.now,null=True,blank=True,)
    # Hostel_About = models.TextField(max_length=500)
    Hostel_lat = models.CharField(max_length=250,blank=True,null=True)
    Hostel_long = models.CharField(max_length=250,blank=True,null=True)
    Hostel_type = models.CharField(max_length=250,blank=True,null=True)
    wifi=models.BooleanField(default=False)
    lodging=models.BooleanField(default=False)
    studyRoom=models.BooleanField(default=False)
    laundary=models.BooleanField(default=False)
    medicalFacility=models.BooleanField(default=False)
    singleRoom=models.BooleanField(default=False)
    dormitory=models.BooleanField(default=False)
    about=models.TextField(max_length=200,blank=True)

    def __str__(self):
        return self.Hostel_name

class Request_Image(models.Model):
    Hostel_image = models.ForeignKey(Hostel_Request, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='image/', blank=True)
    
    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)




