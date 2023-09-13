# Generated by Django 2.2.28 on 2023-09-13 02:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curation_portal', '0019_variant_reads'),
    ]

    operations = [
        migrations.AddField(
            model_name='curationresult',
            name='editor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='edited_results', to=settings.AUTH_USER_MODEL),
        ),
    ]
