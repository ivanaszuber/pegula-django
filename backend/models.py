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
          'User', 'UserRoles'

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
    LVL1_USER = 'Level 1 User'
    LVL2_USER = 'Level 2 User'
    LVL3_USER = 'Level 3 User'

    valid_types = {
        ADMIN, LVL1_USER, LVL2_USER, LVL3_USER
    }

    by_org = {
        ClientType.ADMIN: [ADMIN, LVL1_USER],
        ClientType.LVL1: [LVL1_USER],
        ClientType.LVL2: [LVL2_USER],
        ClientType.LVL3: [LVL3_USER]
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


class Lvl1AdminManager(models.Manager):
    def get_queryset(self):
        return super(Lvl1AdminManager, self).get_queryset().filter(groups__name=UserRoles.LVL1_USER)

    def for_org(self, org_id):
        return self.get_queryset().filter(client__org_id=org_id)


class ClientUserManager(models.Manager):
    def get_queryset(self):
        return super(ClientUserManager, self).get_queryset().filter()

    def for_org(self, org_id):
        return self.get_queryset().filter(client__org_id=org_id)


USER_STATUS = [
    ('active', 'Active'),
    ('deactivated', 'Deactivated')
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
    REQUIRED_FIELDS = ['client']

    client = models.ForeignKey(Client, related_name='users', related_query_name='user', blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True)
    status = models.CharField(choices=USER_STATUS, default='active', max_length=12, db_index=True)

    # Query managers
    objects = PegulaUserManager()
    platform_admins = PegulaAdminManager()
    org_admins = Lvl1AdminManager()
    org_users = ClientUserManager()

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
    def is_org_admin(self):
        return self.groups.filter(name=UserRoles.LVL1_USER).exists()

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
