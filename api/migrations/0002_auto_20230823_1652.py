# Generated by Django 3.2.20 on 2023-08-23 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='data',
        ),
        migrations.RemoveField(
            model_name='auction',
            name='hash',
        ),
        migrations.RemoveField(
            model_name='auction',
            name='txId',
        ),
    ]