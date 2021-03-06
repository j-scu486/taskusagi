# Generated by Django 3.0.8 on 2020-08-03 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_schedulebookingreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulebookingreview',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedulebookingreview',
            name='rating',
            field=models.CharField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)], default=3, max_length=1),
        ),
    ]
