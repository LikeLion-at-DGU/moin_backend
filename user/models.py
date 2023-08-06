from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.dispatch import receiver
from django.db.models.signals import post_save


class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields):
        if username is None:
            raise TypeError('Users must have a username.')

        if password is None:
            raise TypeError('Users must have a password.')

        user = self.model(
            username = username,
            **extra_fields
            )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(null=True, max_length=255, unique=True)
    email = models.EmailField(max_length=30, null=True, blank=True)
    USERNAME_FIELD = 'username'

class Job(models.Model):
    DESIGN = '디자이너'
    IT_DEVELOP = 'IT개발자'
    AI_ENGINEER = '인공지능'

    JOB_CHOICES = (
        (DESIGN, '디자인'),
        (IT_DEVELOP, 'IT'),
        (AI_ENGINEER, '인공지능'),
    )

    name = models.CharField(max_length=100, choices=JOB_CHOICES, unique=True)

    def __str__(self):
        return self.name