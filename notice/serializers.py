from rest_framework import serializers
from .models import *

# 공지사항 이미지
class NotificationImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = NotificationImage
        fields = ['image']
    
# 공지사항 list
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'writer', 'title', 'view_cnt', 'created_at']

# 공지사항 detail
class NotificationDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, instance):
        request=self.context.get('request')
        noticeimage=instance.images_notification.all().order_by('id')
        try:
            noticeimage_serializer=NotificationImageSerializer(noticeimage, many=True)
            outcome = []
            for data in noticeimage_serializer.data:
                image_url = request.build_absolute_uri(data["image"])
                outcome.append(image_url)
            return outcome
        except:
            return None
    
    class Meta:
        model = Notification
        fields = ['id', 'writer', 'title', 'content', 'view_cnt', 'created_at', 'images']