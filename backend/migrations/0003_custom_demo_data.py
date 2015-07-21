from django.db import models, migrations, transaction
from django.contrib.auth.models import Group

from backend.models import *


ORGS = [
    # name, id, type
    ('Client 1', 'client1', ClientType.TYP1),
    ('Client 2', 'client2', ClientType.TYP2),
    ('Client 3', 'client3', ClientType.TYP3),
    ('Client 4', 'client4', ClientType.TYP4)
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
    for name, id, address, phone, type in ORGS:
        org = Client(name=name, id=id, type=type, address=address, phone=phone)
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
