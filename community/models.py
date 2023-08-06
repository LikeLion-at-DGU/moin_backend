from django.db import models
from user.models import Job, User
from main.models import Ai

# Create your models here.
def community_image_upload_path(instance, filename):
    return f'{instance.community.id}/{filename}'

class Community(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE, related_name='community_ai')
    CATEGORY_LIST = (
        ('qna', 'qna'),
        ('common', 'common'),
        ('tip', 'tip'),
    )
    category = models.CharField(max_length=10, choices=CATEGORY_LIST, blank=False, null=False)
    writer = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField(null=True, max_length=5000)
    veiw_cnt = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # 좋아요 관련 기능 추가해야 함

class CommunityComment(models.Model):
    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, blank=False, null=False, on_delete=models.CASCADE, related_name='comments_community')
    writer = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CommunityTempComment(models.Model):
    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, blank=False, null=False, on_delete=models.CASCADE, related_name='temp_comments_community')
    tmp_password = models.CharField(max_length=4)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CommunityImage(models.Model):
    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='images_community')
    image = models.ImageField(upload_to=community_image_upload_path)