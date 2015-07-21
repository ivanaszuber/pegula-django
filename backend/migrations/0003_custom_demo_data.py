from django.db import models, migrations, transaction
from django.contrib.auth.models import Group

from backend.models import *


ORGS = [
    # name, org_id, org_type
    ('Pegula', 'admin', ClientType.ADMIN),
    ('LVL1', 'lvl1', ClientType.LVL1),
    ('LVL2', 'lvl2', ClientType.LVL2),
    ('LVL3', 'lvl3', ClientType.LVL3)
]


USERS = [
    # email/password,     roles
    ('admin@pegula.io', [UserRoles.ADMIN]),
    ('manager@pegula.io', [UserRoles.MNG]),
    ('employee@pegula.io', [UserRoles.EMPL])
]


@transaction.atomic
def create_orgs(apps, schema_editor):
    """Create canned Client"""
    for name, org_id, org_type in ORGS:
        org = Client(name=name, org_id=org_id, org_type=org_type)
        org.save()

@transaction.atomic
def create_users(apps, schema_editor):
    """Create canned Users"""
    for email, roles in USERS:
        password = email.split('@', 1)[0]
        user = User.objects.create_user(email, password=password)
        user.groups.add(*[Group.objects.get(name=role) for role in roles])
        user.full_clean()
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_custom_roles'),
    ]

    operations = [
        migrations.RunPython(create_orgs),
        migrations.RunPython(create_users),
    ]
