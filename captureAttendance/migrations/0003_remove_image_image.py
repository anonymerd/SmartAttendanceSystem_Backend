# Generated by Django 4.0.3 on 2022-03-27 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('captureAttendance', '0002_image_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='image',
        ),
    ]
