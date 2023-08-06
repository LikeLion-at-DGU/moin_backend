from django.db import models
from user.models import User
from main.models import Ai

# Create your models here.
def suggestion_image_upload_path(instance, filename):
    return f'suggestion/{instance.suggestion.id}/{filename}'

class Suggestion(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, blank=False, null=False, on_delete=models.CASCADE, related_name='suggestion_ai')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, max_length=10)
    title = models.CharField(max_length=100)
    content = models.TextField(null=False, max_length=5000)
    url = models.URLField(max_length=100) # 레퍼런스 혹은 원하는 수정 url
    # veiw_cnt = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SuggestionComment(models.Model):
    id = models.AutoField(primary_key=True)
    suggestion = models.ForeignKey(Suggestion, blank=False, null=False, on_delete=models.CASCADE, related_name='comments_suggestion')
    writer = models.CharField(max_length=10, default='admin')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SuggestionImage(models.Model):
    id = models.AutoField(primary_key=True)
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='images_suggestion')
    image = models.ImageField(upload_to=suggestion_image_upload_path)