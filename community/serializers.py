from rest_framework import serializers
from .models import Community, CommunityComment, CommunityImage, CommunityLike
from user.models import User
from django.shortcuts import get_object_or_404

# 이미지
class CommunityImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = CommunityImage
        fields = ['image']

# 댓글
class CommunityCommentSerializer(serializers.ModelSerializer):
    community = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()    

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")
    
    def get_community(self, instance):
        return instance.community.id
    
    def get_writer(self, instance):
        return instance.writer.nickname
    
    class Meta:
        model = CommunityComment
        fields = '__all__'

# 커뮤니티 리스트
class CommunitySerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source='writer.nickname', read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True) 

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_comments_cnt(self, instance):
        return instance.comments_community.count()

    class Meta:
        model = Community
        fields = [
            "id",
            "ai",
            "category",
            "title",
            "writer",
            "comments_cnt",
            "is_liked",
            "likes_cnt",
            "created_at"
        ]

# 커뮤니티 게시물 작성
class CommunityCreateSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source='writer.nickname', read_only=True)
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    created_at = serializers.SerializerMethodField()   

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def create(self, validated_data):
        image_data = self.context['request'].FILES
        user = self.context['request'].user
        validated_data['writer'] = user
        instance = Community.objects.create(**validated_data)
        for image_data in image_data.getlist('image'):
            CommunityImage.objects.create(community=instance, image=image_data)
        return instance
    
    class Meta:
        model = Community
        fields = ['id', 'ai', 'writer', 'category', 'title', 'content', 'images', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommunityDetailSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source='writer.nickname', read_only=True)
    ai = serializers.CharField(source='ai.title', read_only=True)
    images = serializers.SerializerMethodField()
    is_liked = serializers.BooleanField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()    

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")

    # 등록된 이미지들 가져오기
    def get_images(self, obj):
        image = obj.images_community.all()
        return CommunityImageSerializer(instance=image, many=True, context=self.context).data

    class Meta:
        model = Community
        fields = [
            'id', 
            'ai',
            'category',
            'writer', 
            'title', 
            'content', 
            'is_liked', 
            'likes_cnt', 
            'images', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at'
        ]

