from django.db import models
from uuid import uuid4
import os


class Image(models.Model):
    # image = models.ImageField(upload_to="uploads/")
    image = models.FileField(upload_to='uploads/', null=True)
    name = models.TextField(default="DEFAULT")
    created = models.DateTimeField(auto_now=True)


def path_and_rename(instance, filename):
    upload_to = 'images'
    ext = filename.split('.')[-1]
    # get filename
    print(instance)
    if instance.empId:
        filename = '{}.{}'.format(instance.empId, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class Employee(models.Model):
    # image = models.ImageField(upload_to="uploads/")
    empId = models.TextField(primary_key=True)
    image = models.FileField(upload_to=path_and_rename, null=True)
    name = models.TextField(default="DEFAULT_Name")
    created = models.DateTimeField(auto_now=True)
