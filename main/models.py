from django.db import models
from user.models import User
# Create your models here.
def thumbnail_image_upload_path(instance):
    return f'{instance.title}'

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

class Ai(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30)
    url = models.URLField(max_length=100)
    thumbnail = models.ImageField(blank=True, null=True)
    company = models.CharField(max_length=20, null=True)
    veiw_cnt = models.PositiveIntegerField()
    content = models.TextField(null=True, max_length=1000)
    applier = models.CharField(max_length=10,default='admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AiComment(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE, related_name='comments_ai')
    writer = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, related_name='comments')
    rating = models.PositiveIntegerField(null=True)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AiTempComment(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE, related_name='temp_comments_ai')
    tmp_password = models.CharField(max_length=4)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Keyword(models.Model):
    id = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length=30)

class AiKeywordTable(models.Model):
    id = models.AutoField(primary_key=True)
    keyword = models.ForeignKey(Keyword, blank=False, null=False, on_delete=models.CASCADE)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE)

class AiLikeTable(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, related_name='comments')
    job = models.ForeignKey(Job, blank=False, null=False, on_delete=models.CASCADE)

class AiJobTable(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, blank=False, null=False, on_delete=models.CASCADE)
