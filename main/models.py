from django.db import models
from user.models import Job, User
# Create your models here.
def thumbnail_image_upload_path(instance):
    return f'main/{instance.title}'

class Keyword(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

class Ai(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30)
    keyword = models.ManyToManyField(Keyword, related_name='keywords')
    url = models.URLField(max_length=100)
    thumbnail = models.ImageField(blank=True, null=True)
    company = models.CharField(max_length=20, null=True)
    view_cnt = models.PositiveIntegerField(default=0)
    content = models.TextField(null=True, max_length=1000)
    applier = models.CharField(max_length=10,default='admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class AiComment(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE, related_name='comments_ai')
    is_tmp = models.BooleanField(null=True,default=False)
    tmp_password = models.CharField(max_length=4,blank=True,null=True)
    writer = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AiRating(models.Model):
    id = models.AutoField(primary_key=True)
    rating = models.IntegerField(null=True, blank=True, default=None)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE, related_name='rating_ai')
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, related_name='rating_user')

class AiLike(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, related_name='likes')
    job = models.ForeignKey(Job, blank=False, null=True, on_delete=models.DO_NOTHING)
