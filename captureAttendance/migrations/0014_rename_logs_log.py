# Generated by Django 4.0.3 on 2022-04-29 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('captureAttendance', '0013_rename_empid_user_userid_logs'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Logs',
            new_name='Log',
        ),
    ]
