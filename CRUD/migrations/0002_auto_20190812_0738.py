# Generated by Django 2.1.8 on 2019-08-12 14:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('CRUD', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostel_request',
            name='Hostel_Estd',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Date ESTD'),
        ),
        migrations.AlterField(
            model_name='hostel_request',
            name='Hostel_Price',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
