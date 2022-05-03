from itertools import count
from statistics import mode
from django.db import models
from uuid import uuid4
import os


def path_and_rename(instance, filename, upload_to):
    # upload_to = 'images'
    ext = filename.split('.')[-1]
    # get filename
    print(instance)
    if instance.id:
        filename = '{}.{}'.format(instance.id, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


def path_and_rename_company(instance, filename):
    return path_and_rename(instance, filename, 'images/company')


def path_and_rename_user(instance, filename):
    return path_and_rename(instance, filename, 'images/user')


class Image(models.Model):
    image = models.FileField(upload_to='uploads/', null=True)
    name = models.TextField(default="DEFAULT")
    created = models.DateTimeField(auto_now=True)


class Company(models.Model):
    
    id = models.AutoField(auto_created=True, primary_key=True)
    companyId = models.TextField(unique=True)
    name = models.TextField()
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to=path_and_rename_company, null=True)
    city = models.TextField()
    country = models.TextField()
    isApproved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True) 

class User(models.Model):
    USER_TYPE_CHOICES = [
        ('EMP', 'Employee'),
        ('AD', 'Admin'),
        ('SA', 'SuperAdmin'),
        ('NONE', 'None')
    ]

    id = models.AutoField(auto_created=True, primary_key=True)
    userId = models.TextField(unique=True)
    name = models.TextField(default="DEFAULT_Name")
    email = models.EmailField(unique=True)
    password = models.TextField(null=True)
    # image = models.ImageField(upload_to='images', null=True)
    image = models.ImageField(upload_to=path_and_rename_user, null=True)
    userType = models.TextField(choices=USER_TYPE_CHOICES)
    designation = models.TextField()
    companyId = models.ForeignKey(
        'Company', to_field='companyId', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Log(models.Model):
    LOGS_TYPE_CHOICES = [
        ('CI', 'CheckIn'),
        ('CO', 'CheckOut')
    ]

    id = models.AutoField(auto_created=True, primary_key=True)
    userId = models.ForeignKey(
        'User', to_field='userId', on_delete=models.CASCADE)
    companyId = models.ForeignKey(
        'Company', to_field='companyId', on_delete=models.CASCADE)
    type = models.TextField(choices=LOGS_TYPE_CHOICES)
    datetime = models.DateTimeField()
    location = models.TextField()
