# Generated by Django 3.0.8 on 2020-09-06 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messageinstance',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='messageinstance',
            name='message',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.DeleteModel(
            name='MessageInstance',
        ),
    ]