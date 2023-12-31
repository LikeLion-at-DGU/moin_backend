from rest_framework import serializers
from .models import Community, CommunityComment, CommunityImage, CommunityLike
from django.contrib.auth import get_user_model
from main.models import Ai, AiComment

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
    # is_liked = serializers.SerializerMethodField(read_only=True)
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
    
    # def get_is_liked(self, instance):
    #     User = get_user_model()
    #     user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
    #     if user is not None:
    #         return CommunityLike.objects.filter(community=instance,user=user).exists()
    #     else:
    #         return False
    
    class Meta:
        model = Community
        fields = [
            "id",
            "ai",
            "category",
            "title",
            # "writer",
            "comments_cnt",
            "view_cnt",
            # "is_liked",
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
    ai = serializers.SerializerMethodField(read_only=True)

    def get_ai(self, instance):
        ai_instance = instance.ai
        if ai_instance is not None:
            if ai_instance.title:
                return ai_instance.title
            else:
                return "기타"
        else:
            return "기타"

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
            "view_cnt",
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
    ai = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    def clear_existing_images(self, instance):
        for community_image in instance.images_community.all():
            community_image.image.delete()
            community_image.delete()

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")
    
    def create(self, validated_data):
        category = validated_data.get('category')
        ai_title = validated_data.get('ai')

        if category == 'tip' and (ai_title is None or ai_title == ""):
            raise serializers.ValidationError("꿀팁 게시물을 작성할 때는 AI 제목을 입력해주세요.")

        ai_instance = None
        if ai_title:
            try:
                ai_instance = Ai.objects.get(title=ai_title)
            except Ai.DoesNotExist:
                raise serializers.ValidationError("존재하지 않는 ai입니다.")
        
        image_data = self.context['request'].FILES
        user = self.context['request'].user
        validated_data['writer'] = user
        validated_data['ai'] = ai_instance 
        instance = Community.objects.create(**validated_data)
        for image_data in image_data.getlist('image'):
            CommunityImage.objects.create(community=instance, image=image_data)
        return instance
    
    def update(self, instance, validated_data):
        ai_title = validated_data.get('ai')

        ai_instance = None
        if ai_title:
            try:
                ai_instance = Ai.objects.get(title=ai_title)
            except Ai.DoesNotExist:
                raise serializers.ValidationError("존재하지 않는 ai입니다.")
        
        image_data = self.context['request'].FILES
        validated_data['ai'] = ai_instance 
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
    ai = serializers.SerializerMethodField(read_only=True)

    def get_ai(self, instance):
        ai_instance = instance.ai
        if ai_instance is not None:
            if ai_instance.title:
                return ai_instance.title
            else:
                return "기타"
        else:
            return "기타"

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
class MyAllPostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category = serializers.SerializerMethodField()
    title = serializers.CharField()
    # likes_cnt = serializers.IntegerField(read_only=True)
    # comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)  

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")
    
    # def get_comments_cnt(self, instance):
    #     if isinstance(instance, Community):
    #         return instance.comments_community.count()
    #     elif isinstance(instance, Suggestion):
    #         return instance.comments_suggestion.count()
    #     return 0
        
    # def get_likes_cnt(self, instance):
    #     if isinstance(instance, Community):
    #         return instance.likes_community.count()
    #     elif isinstance(instance, Suggestion):
    #         return instance.likes_suggestion.count()
    #     return 0
        
    def get_category(self, instance):
        if isinstance(instance, Community):
            return instance.category
        elif isinstance(instance, Suggestion):
            return "건의사항"
        return None
    
    class Meta:
        fields = [
            "id",
            "category",
            "title",
            # "comments_cnt",
            # "likes_cnt",
            "created_at"
        ]

# 내가 작성한 게시물 중 커뮤니티 tip, common, qna 
class MyPostCommunityListSerializer(serializers.ModelSerializer):
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
            "category",
            "title",
            "comments_cnt",
            "likes_cnt",
            "created_at"
        ]

# 내가 작성한 댓글
class MyCommunityCommentSerializer(serializers.ModelSerializer):
    community_id = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    updated_at = serializers.SerializerMethodField(read_only=True)  
    category = serializers.SerializerMethodField(read_only=True)  

    def get_community_id(self, instance):
        return instance.community.id

    def get_category(self, instance):
        return instance.community.category

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")
    
    def get_community(self, instance):
        return instance.community.id
    
    class Meta:
        model = CommunityComment
        fields = ['id', 'community_id', 'category', 'content', 'created_at', 'updated_at']

# 내 모든 댓글(커뮤+ai후기)
class MyAllCommentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    content = serializers.CharField()
    # likes_cnt = serializers.IntegerField(read_only=True)
    # comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)  
    # updated_at = serializers.SerializerMethodField(read_only=True)     

    def get_type(self, instance):
        if isinstance(instance, CommunityComment):
            return instance.community.id  # 댓글이 커뮤니티 댓글인 경우 커뮤니티의 id를 반환
        elif isinstance(instance, AiComment):
            return instance.ai.title  # 댓글이 ai 후기인 경우 해당 ai의 title을 반환
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if isinstance(instance, CommunityComment):
            data['community_id'] = instance.community.id
            del data['type']
        elif isinstance(instance, AiComment):
            data['ai'] = instance.ai.title
            del data['type']

        return data

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    # def get_updated_at(self, instance):
    #     return instance.updated_at.strftime("%Y/%m/%d %H:%M")
    
    def get_category(self, instance):
        if isinstance(instance, CommunityComment):
            return instance.community.category
        elif isinstance(instance, AiComment):
            return "ai"
        return None
    
    class Meta:
        fields = [
            "id",
            "category",
            "type",
            "content",
            "created_at",
            # "updated_at"
        ]