# Generated by Django 2.2.5 on 2019-09-09 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20190909_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='task_done_date',
            field=models.DateTimeField(null=True, verbose_name='done date'),
        ),
    ]