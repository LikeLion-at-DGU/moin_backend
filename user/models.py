from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    # 일반 user 생성
    def create_user(self, email, nickname, job, password, description=None):
        if not email:
            raise ValueError('must have user email')
        if not nickname:
            raise ValueError('must have user nickname')
        if not job:
            raise ValueError('must have user job')
        user = self.model(
            email = self.normalize_email(email),
            nickname = nickname,
            job = job,
            description = description
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # 관리자 user 생성
    def create_superuser(self, email, nickname, password, job=None, description=None):
        user = self.create_user(
            email,
            password = password,
            nickname = nickname,
            job = Job.objects.get(job=1),
            description = description
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Job(models.Model):
    #id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(default='', max_length=100, null=False, blank=False, unique=True)
    nickname = models.CharField(default='', max_length=100, null=False, blank=False, unique=True)
    description = models.CharField(default='', max_length=100, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)    
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    # 헬퍼 클래스 사용
    objects = UserManager()

    # 사용자의 username field는 email
    USERNAME_FIELD = 'email'
    # 필수로 작성해야 하는 field
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.email