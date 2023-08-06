from django.db import models

# Create your models here.
def notification_image_upload_path(instance, filename):
    return f'{instance.notification.id}/{filename}'

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    writer = models.CharField(max_length=10, default='admin')
    title = models.CharField(max_length=20)
    content = models.CharField(max_length=5000)
    veiw_cnt = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class NotificationImage(models.Model):
    id = models.AutoField(primary_key=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='images_notification')
    image = models.ImageField(upload_to=notification_image_upload_path)