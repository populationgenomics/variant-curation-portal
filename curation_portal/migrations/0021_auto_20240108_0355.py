# Generated by Django 2.2.28 on 2024-01-08 03:55

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curation_portal', '0020_curationresult_editor'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='AD',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=2), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='variant',
            name='AD_all',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=2), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='variant',
            name='DP_all',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='variant',
            name='GQ_all',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
    ]
