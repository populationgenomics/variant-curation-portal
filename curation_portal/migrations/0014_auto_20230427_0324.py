# Generated by Django 2.2.24 on 2023-04-27 03:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("curation_portal", "0013_customflag_customflagcurationresult"),
    ]

    operations = [
        migrations.RenameField(
            model_name="usersettings",
            old_name="ucsc_session_name",
            new_name="ucsc_session_name_grch37",
        ),
    ]
