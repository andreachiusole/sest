# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-22 23:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sest', '0007_auto_20170123_0026'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='field_no',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
    ]