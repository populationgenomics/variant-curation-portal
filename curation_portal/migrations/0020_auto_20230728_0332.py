# Generated by Django 2.2.24 on 2023-07-28 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curation_portal", "0017_auto_20230726_0322"),
    ]

    operations = [
        migrations.AlterField(
            model_name="variantannotation",
            name="hgvsc",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="variantannotation",
            name="hgvsp",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
