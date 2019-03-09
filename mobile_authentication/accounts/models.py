from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import time


def update_last_login(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        """
        Create and save a user with the given phone number and password.
        """
        if not phone_number:
            raise ValueError('The given phone number must be set')

        phone_number = self.model.normalize_username(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    display_name = models.CharField(_('Display name'), max_length=150, blank=True)
    phone_number = models.CharField(_('Phone number'), max_length=15, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class PhoneOTP(models.Model):
    # phone_regex = RegexValidator(regex=r'^\+?234?\d(9,14)$',
    #     message="Phone number must be entered in format of +2348044234244 up to 14 digits")
    # phone = models.CharField(validator=[phone_regex], max_length=15, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    initial = models.IntegerField(blank=True, null=True)
    elapse = models.IntegerField(blank=True, null=True)
    validated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.phone_number} is sent {self.otp}'


def add_elaspe(sender, instance, *args, **kwargs):
    instance.initial = int(time.time())
    instance.elapse = instance.initial + 30



pre_save.connect(add_elaspe, sender=PhoneOTP)
