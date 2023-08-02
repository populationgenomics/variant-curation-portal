# Generated by Django 2.2.24 on 2023-07-26 03:22

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("curation_portal", "0016_auto_20230614_0004"),
    ]

    operations = [
        migrations.AddField(
            model_name="variant",
            name="DP",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(blank=True, null=False),
                blank=True,
                null=True,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="variant",
            name="GQ",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(blank=True, null=False),
                blank=True,
                null=True,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="variant",
            name="GT",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, max_length=1000, null=False),
                blank=True,
                null=True,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="variant",
            name="n_heterozygotes",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="variant",
            name="sample_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, max_length=1000, null=False),
                blank=True,
                null=True,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="variantannotation",
            name="appris",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="variantannotation",
            name="exon",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="variantannotation",
            name="hgvsc",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="variantannotation",
            name="hgvsp",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="variantannotation",
            name="mane_select",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
