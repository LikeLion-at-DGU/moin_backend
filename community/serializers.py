from rest_framework import serializers
from .models import Community, CommunityComment, CommunityImage, CommunityLike
from django.contrib.auth import get_user_model

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

# 커뮤니티 리스트 - 꿀팁
class TipListSerializer(serializers.ModelSerializer):
    # writer = serializers.CharField(source='writer.nickname', read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True) 
    ai = serializers.SerializerMethodField(read_only=True)

    def get_ai(self, instance):
        ai_instance = instance.ai
        if ai_instance is not None:
            return ai_instance.title
        else:
            return None
    
    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_comments_cnt(self, instance):
        return instance.comments_community.count()
    
    def get_is_liked(self, instance):
        User = get_user_model()
        user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
        if user is not None:
            return CommunityLike.objects.filter(community=instance,user=user).exists()
        else:
            return False
    
    class Meta:
        model = Community
        fields = [
            "id",
            "ai",
            "category",
            "title",
            # "writer",
            "comments_cnt",
            "is_liked",
            "likes_cnt",
            "created_at"
        ]

# 커뮤니티 리스트 - 자유, qna
class CommonQnaListSerializer(serializers.ModelSerializer):
    # writer = serializers.CharField(source='writer.nickname', read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    
    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_comments_cnt(self, instance):
        return instance.comments_community.count()
    
    def get_is_liked(self, instance):
        User = get_user_model()
        user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
        if user is not None:
            return CommunityLike.objects.filter(community=instance,user=user).exists()
        else:
            return False

    class Meta:
        model = Community
        fields = [
            "id",
            "category",
            "title",
            # "writer",
            "comments_cnt",
            "is_liked",
            "likes_cnt",
            "created_at"
        ]

# 커뮤니티 게시물 작성, 수정
class CommunityCreateUpdateSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source='writer.nickname', read_only=True)
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def clear_existing_images(self, instance):
        for community_image in instance.images_community.all():
            community_image.image.delete()
            community_image.delete()

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")
    
    def create(self, validated_data):
        image_data = self.context['request'].FILES
        user = self.context['request'].user
        validated_data['writer'] = user
        instance = Community.objects.create(**validated_data)
        for image_data in image_data.getlist('image'):
            CommunityImage.objects.create(community=instance, image=image_data)
        return instance
    
    def update(self, instance, validated_data):
        image_data = self.context['request'].FILES
        self.clear_existing_images(instance)
        for image_data in image_data.getlist('image'):
            CommunityImage.objects.create(community=instance, image=image_data)
        return super().update(instance, validated_data)

    class Meta:
        model = Community
        fields = ['id', 'ai', 'writer', 'category', 'title', 'content', 'images', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# 커뮤니티 디테일 - 자유게시판
class CommonDetailSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source='writer.nickname', read_only=True)
    images = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()    

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")

    def get_comments_cnt(self, instance):
        return instance.comments_community.count()
    
    def get_is_liked(self, instance):
        User = get_user_model()
        user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
        if user is not None:
            return CommunityLike.objects.filter(community=instance,user=user).exists()
        else:
            return False
        
    # 등록된 이미지들 가져오기
    def get_images(self, obj):
        image = obj.images_community.all()
        return CommunityImageSerializer(instance=image, many=True, context=self.context).data

    class Meta:
        model = Community
        fields = [
            'id', 
            'category',
            'writer', 
            'title', 
            'content', 
            'is_liked', 
            'view_cnt',
            'comments_cnt',
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

# 커뮤니티 디테일 - qna, 꿀팁
class QnaTipDetailSerializer(serializers.ModelSerializer):
    ai = serializers.CharField(source='ai.title', read_only=True)
    writer = serializers.CharField(source='writer.nickname', read_only=True)
    images = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()    

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")

    def get_comments_cnt(self, instance):
        return instance.comments_community.count()
    
    def get_is_liked(self, instance):
        User = get_user_model()
        user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
        if user is not None:
            return CommunityLike.objects.filter(community=instance,user=user).exists()
        else:
            return False


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
            'view_cnt',
            'comments_cnt',
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


## 임시
class CommunitySerializer(serializers.ModelSerializer):
    # writer = serializers.CharField(source='writer.nickname', read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True) 

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")
    
    def get_comments_cnt(self, instance):
        return instance.comments_community.count()
    
    def get_is_liked(self, instance):
        User = get_user_model()
        user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
        if user is not None:
            return CommunityLike.objects.filter(community=instance,user=user).exists()
        else:
            return False
        
    class Meta:
        model = Community
        fields = [
            "id",
            "ai",
            "category",
            "title",
            # "writer",
            "comments_cnt",
            "is_liked",
            "likes_cnt",
            "created_at"
        ]

## 마이페이지 관련 시리얼라이저
from itertools import chain
from suggestion.models import Suggestion

# 내가 작성한 전체 게시물 목록 조회(커뮤+건의)
class MyAllPostSerializer(serializers.ModelSerializer):
    is_liked = serializers.BooleanField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True) 

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")
    
    def get_comments_cnt(self, instance):
        return instance.comments_community.count()
    
    def get_is_liked(self, instance):
        User = get_user_model()
        user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
        if user is not None:
            return CommunityLike.objects.filter(community=instance,user=user).exists()
        else:
            return False
        
    class Meta:
        model = Community
        fields = [
            "id",
            "category",
            "title",
            "comments_cnt",
            "is_liked",
            "likes_cnt",
            "created_at"
        ]

# 내가 작성한 게시물 중 커뮤니티 tip, common, qna 
class MyPostCommunityListSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True) 
    
    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_comments_cnt(self, instance):
        return instance.comments_community.count()
    
    def get_is_liked(self, instance):
        User = get_user_model()
        user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
        if user is not None:
            return CommunityLike.objects.filter(community=instance,user=user).exists()
        else:
            return False
    
    class Meta:
        model = Community
        fields = [
            "id",
            "category",
            "title",
            "comments_cnt",
            "is_liked",
            "likes_cnt",
            "created_at"
        ]