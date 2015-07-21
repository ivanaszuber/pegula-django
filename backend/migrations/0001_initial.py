# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import backend.models


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(
                    help_text='Designates that this user has all permissions without explicitly assigning them.',
                    default=False, verbose_name='superuser status')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=48, unique=True, db_index=True,
                                            error_messages={'unique': 'A user with that email address already exists.'},
                                            verbose_name='email address')),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.',
                                                 default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(
                    help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                    default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(max_length=24, blank=True)),
                ('status', models.CharField(default='active', max_length=12, db_index=True,
                                            choices=[('active', 'Active'), ('deactivated', 'Deactivated')])),
                ('groups', models.ManyToManyField(
                    help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                    to='auth.Group', blank=True, related_name='user_set', related_query_name='user',
                    verbose_name='groups')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            managers=[
                ('objects', backend.models.PegulaUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=48, unique=True, db_index=True,
                                            error_messages={'unique': 'A user with that email address already exists.'},
                                            verbose_name='email address')),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('is_active', models.BooleanField(
                    help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                    default=True, verbose_name='active')),
                ('date_from', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date from')),
                ('date_to', models.DateTimeField(blank=True, null=True, default=django.utils.timezone.now,
                                                 verbose_name='date to')),
                ('role', models.CharField(max_length=30, blank=True, verbose_name='role')),
                ('phone', models.CharField(max_length=24, blank=True)),
                ('status', models.CharField(default='active', max_length=12, db_index=True,
                                            choices=[('Full Time', 'Full TIme'), ('Contract', 'Contract'),
                                                     ('Candidate', 'Candidate'), ('Deactivated', 'Deactivated')]))
            ],
            options={
                'verbose_name_plural': 'employees',
                'verbose_name': 'employee',
            }
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', models.SlugField(max_length=16, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('address', models.CharField(max_length=128)),
                ('phone', models.CharField(max_length=64)),
                ('type',
                 models.CharField(help_text='Possible values: lvl1, lvl2, lvl3, admin', max_length=10, db_index=True,
                                  choices=[('admin', 'Administrators'), ('lvl1', 'LVL1'), ('lvl2', 'LVL2'),
                                           ('lvl3', 'LVL3')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(help_text='Specific permissions for this user.', to='auth.Permission',
                                         blank=True, related_name='user_set', related_query_name='user',
                                         verbose_name='user permissions'),
        ),
    ]
