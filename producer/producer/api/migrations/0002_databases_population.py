# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def populate_databases(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Database = apps.get_model("api", "Database")

    for name, ip in settings.CONSUMERS.items():
        Database.objects.create(name=name, ip=ip)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_databases),
    ]
