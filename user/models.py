from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password, job, nickname, description=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address.')
        
        user = self.model(
            email=email,
            job=job,
            nickname=nickname,
            description=description,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

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

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    job = models.ForeignKey(Job, on_delete=models.DO_NOTHING, null=False, blank=False)
    nickname = models.CharField(max_length=10, null=False, blank=False)
    description = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 헬퍼 클래스
    objects = UserManager()

    # 사용자의 username field를 email로 설정(이메일로 로그인)
    USERNAME_FIELD = 'email'