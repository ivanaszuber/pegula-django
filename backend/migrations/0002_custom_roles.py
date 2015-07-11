from django.db import models, migrations, transaction
from django.contrib.auth.models import Group

from backend.models import UserRoles


@transaction.atomic
def create_roles(apps, schema_editor):
    """Create our system Roles (Django Groups)"""
    for name in UserRoles.valid_types:
        Group(name=name).save()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]
