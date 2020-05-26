# Generated by Django 3.0.5 on 2020-05-25 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slogger', '0011_auto_20200524_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='date_range_days_details',
            field=models.IntegerField(default=7, verbose_name='Default summary date range (details)'),
        ),
        migrations.AddField(
            model_name='usersettings',
            name='show_meal_durations',
            field=models.BooleanField(default=True, verbose_name='Show durations for meals'),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='date_range_days',
            field=models.IntegerField(default=14, verbose_name='Default summary date range (summary)'),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='use_new_ui',
            field=models.BooleanField(default=True, verbose_name='Use new UI variant'),
        ),
    ]