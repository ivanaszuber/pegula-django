import logging

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import ugettext_lazy as _


class TimestampedModel(models.Model):
    """Abstract base Model which provides auto-updating `created` and `modified` fields"""
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


__all__ = 'Client', 'ClientType', \
          'User', 'UserRoles', 'Employee'

log = logging.getLogger(__name__)


#
# Clients
#

class ClientType:
    ADMIN = 'admin'
    LVL1 = 'lvl1'
    LVL2 = 'lvl2'
    LVL3 = 'lvl3'

    valid_types = {ADMIN, LVL1, LVL2, LVL3}

    choices = (
        (ADMIN, 'Pegula Administrators'),
        (LVL1, 'Level 2 access'),
        (LVL2, 'Level 2 access'),
        (LVL3, 'Level 3 access')
    )


class Client(TimestampedModel):
    """A top-level Organization, which serves as a collection of `OrgUsers`"""
    org_id = models.SlugField(unique=True, max_length=16, primary_key=True)
    name = models.CharField(max_length=64, blank=False)
    org_type = models.CharField(choices=ClientType.choices, max_length=10, db_index=True, blank=False,
                                help_text='Possible values: ' + ', '.join(ClientType.valid_types))

    # Query managers
    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.org_id:
            self.org_id = slugify(self.name)
        return super(Client, self).save(*args, **kwargs)


#
# User
#

class UserRoles:
    ADMIN = 'Administrator'
    MNG = 'Manager'
    EMPL = 'Employee'

    valid_types = {
        ADMIN, MNG, EMPL
    }


class PegulaUserManager(BaseUserManager):
    # See: https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#django.contrib.auth.models.CustomUserManager

    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves a User with the given email, password, etc."""
        now = timezone.now()
        email = self.normalize_email(email)
        if not email:
            raise ValueError('Email address must be set')
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, date_joined=now,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

    def get_by_email(self, email):
        users = super(PegulaUserManager, self).get_queryset().filter(email=email)
        return users[0] if users else None


class PegulaAdminManager(models.Manager):
    def get_queryset(self):
        return super(PegulaAdminManager, self).get_queryset().filter(groups__name=UserRoles.ADMIN)


USER_STATUS = [
    ('active', 'Active'),
    ('deactivated', 'Deactivated')
]

EMPLOYEE_STATUS = [
    ('Full Time', 'Full TIme'),
    ('Contract', 'Contract'),
    ('Candidate', 'Candidate'),
    ('Deactivated', 'Deactivated')
]


class User(TimestampedModel, AbstractBaseUser, PermissionsMixin):
    # See: https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#specifying-a-custom-user-model
    # This class partially duplicates/overrides the model provided by Django's `AbstractUser`
    email = models.EmailField(_('email address'), max_length=48, unique=True, blank=False, db_index=True,
                              error_messages={
                                  'unique': _("A user with that email address already exists."),
                              })
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'

    phone = models.CharField(max_length=24, blank=True)
    status = models.CharField(choices=USER_STATUS, default='active', max_length=12, db_index=True)

    # Query managers
    objects = PegulaUserManager()
    platform_admins = PegulaAdminManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_platform_admin(self):
        return self.groups.filter(name=UserRoles.ADMIN).exists()

    @property
    def is_org_user(self):
        return not self.is_platform_admin

    def deactivate(self):
        self.status = 'deactivated'
        self.is_active = False

    def reactivate(self):
        """Reactivate a deactivated user account"""
        self.status = 'active'
        self.is_active = True

    def clean(self):
        if self.is_platform_admin:
            self.is_staff = True
            self.is_superuser = True
        super(User, self).clean()

    def __str__(self):
        return self.email


class Employee(TimestampedModel):
    email = models.EmailField(_('email address'), max_length=48, unique=True, blank=False, db_index=True,
                              error_messages={
                                  'unique': _("An employee with that email address already exists.")
                              })
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    role = models.CharField(_('role'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_from = models.DateTimeField(_('date from'), default=timezone.now)
    date_to = models.DateTimeField(_('date to'), blank=True, null=True, default=timezone.now)

    phone = models.CharField(max_length=24, blank=True)
    status = models.CharField(choices=EMPLOYEE_STATUS, max_length=12, db_index=True)

    objects = models.Manager()

    def create_employee(self, email, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        email = self.normalize_email(email)
        if not email:
            raise ValueError('Email address must be set')
        employee = self.model(email=email,
                              is_staff=is_staff, is_active=True,
                              is_superuser=is_superuser, date_from=now,
                              **extra_fields)
        employee.save(using=self._db)
        return employee

    def get_by_email(self, email):
        employees = super(Employee, self).get_queryset().filter(email=email)
        return employees[0] if employees else None

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the employee."""
        return self.first_name

    def deactivate(self):
        self.status = 'deactivated'
        self.is_active = False

    def clean(self):
        super(Employee, self).clean()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        return super(Employee, self).save(*args, **kwargs)
