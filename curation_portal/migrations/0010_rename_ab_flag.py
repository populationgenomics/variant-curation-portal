# Generated by Django 2.2.20 on 2021-05-06 13:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("curation_portal", "0009_add_flags")]

    operations = [
        migrations.RenameField(
            model_name="curationresult", old_name="flag_ab_filter", new_name="flag_skewed_ab"
        )
    ]
