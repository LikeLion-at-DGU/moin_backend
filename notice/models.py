from django.db import models

# Create your models here.
def notification_image_upload_path(instance, filename):
    return f'notification/{instance.notification.id}/{filename}'

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    writer = models.CharField(max_length=10, default='관리자')
    title = models.CharField(max_length=50)
    content = models.TextField(null=False, max_length=5000)
    view_cnt = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class NotificationImage(models.Model):
    id = models.AutoField(primary_key=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='images_notification')
    image = models.ImageField(upload_to=notification_image_upload_path)