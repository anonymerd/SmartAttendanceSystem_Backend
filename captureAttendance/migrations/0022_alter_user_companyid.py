# Generated by Django 4.0.3 on 2022-05-01 21:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('captureAttendance', '0021_alter_company_companyid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='companyId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='captureAttendance.company'),
        ),
    ]