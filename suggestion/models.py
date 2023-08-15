from django.db import models
from user.models import User
from main.models import Ai

# Create your models here.
def suggestion_image_upload_path(instance, filename):
    return f'suggestion/{instance.suggestion.id}/{filename}'

class Suggestion(models.Model):
    id = models.AutoField(primary_key=True)
    ai = models.ForeignKey(Ai, null=True, on_delete=models.CASCADE, related_name='suggestion_ai')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, max_length=10)
    title = models.CharField(max_length=100)
    content = models.TextField(null=False, max_length=5000)
    url = models.CharField(max_length=100, blank=True) # 레퍼런스 혹은 수정을 원하는 url
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status_choices = [
        (0, '대기중'),
        (1, '반영'),
        (2, '미반영'),
    ]
    reflected_status = models.PositiveSmallIntegerField(choices=status_choices, default=0)

    def __str__(self):
        return self.title

class SuggestionComment(models.Model):
    id = models.AutoField(primary_key=True)
    suggestion = models.ForeignKey(Suggestion, blank=False, null=False, on_delete=models.CASCADE, related_name='comments_suggestion')
    writer = models.CharField(max_length=10, default='moin')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SuggestionImage(models.Model):
    id = models.AutoField(primary_key=True)
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='images_suggestion')
    image = models.ImageField(upload_to=suggestion_image_upload_path)