# Generated by Django 2.2.24 on 2023-07-26 06:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curation_portal', '0017_auto_20230726_0322'),
    ]

    operations = [
        migrations.RenameField(
            model_name='variant',
            old_name='sample_ids',
            new_name='sampleIDs',
        ),
    ]
