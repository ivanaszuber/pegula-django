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
    # email/password,             org_id,        roles
    ('admin@pegula.io',         'admin',     [UserRoles.ADMIN]),
    ('lvl1@pegula.io', 'lvl1', [UserRoles.ADMIN, UserRoles.PROJ_MNG]),
    ('lvl2@pegula.io', 'lvl2', [UserRoles.ADMIN, UserRoles.ORG_MNG]),
    ('lvl3@pegula.io', 'lvl3', [UserRoles.EMP_MNG])
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
    for email, orgname, roles in USERS:
        password = email.split('@', 1)[0]
        org = Client.objects.get(org_id=orgname)
        user = User.objects.create_user(email, password=password, client=org)
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
