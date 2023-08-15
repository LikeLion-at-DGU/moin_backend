from rest_framework import serializers
from .models import *

# 건의사항 이미지
class SuggestionImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = SuggestionImage
        fields = ['image']
    
# 건의사항 list
class SuggestionSerializer(serializers.ModelSerializer):
    # list는 이렇게 ..
    writer = serializers.CharField(source='writer.nickname')
    ai = serializers.CharField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    
    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")
    
    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")

    class Meta:
        model = Suggestion
        fields = ['id', 'ai', 'writer', 'title', 'reflected_status', 'created_at', 'updated_at']

# 건의사항 create
class SuggestionCreateSerailizer(serializers.ModelSerializer):
    writer = serializers.CharField(source='writer.nickname', read_only=True)
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    created_at = serializers.SerializerMethodField()
    ai = serializers.CharField()

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def create(self, validated_data):
        ai_title = validated_data.get('ai')

        try:
            ai_instance = Ai.objects.get(title=ai_title)
        except Ai.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 ai입니다.")
    
        image_data = self.context['request'].FILES
        validated_data['ai'] = ai_instance      
        instance = Suggestion.objects.create(**validated_data)
        for image_data in image_data.getlist('image'):
            SuggestionImage.objects.create(suggestion=instance, image=image_data)
        return instance
    
    class Meta:
        model = Suggestion
        fields = ['id', 'ai', 'writer', 'title', 'content', 'url', 'images', 'created_at', 'reflected_status']
        read_only_fields = ['id', 'created_at', 'reflected_status']

# 건의사항 detail
class SuggestionDetailSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source='writer.nickname', read_only=True)
    ai = serializers.CharField(source='ai.title', read_only=True)
    images = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()    

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")

    def get_comments(self, instance):
        serializer = SuggestionCommentSerializer(instance.comments_suggestion, many=True)
        return serializer.data

    # 등록된 이미지들 가져오기
    def get_images(self, obj):
        image = obj.images_suggestion.all()
        return SuggestionImageSerializer(instance=image, many=True, context=self.context).data

    class Meta:
        model = Suggestion
        fields = ['id', 'ai', 'writer', 'title', 'content', 'url', 'comments', 'images', 'created_at', 'updated_at', 'reflected_status']
        read_only_fields = ['id', 'created_at', 'comments', 'updated_at', 'reflected_status']

class SuggestionCommentSerializer(serializers.ModelSerializer):
    suggestion = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()    

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")
    
    def get_suggestion(self, instance):
        return instance.suggestion.id
    
    def get_writer(self, instance):
        return instance.writer
    
    class Meta:
        model = SuggestionComment
        fields = '__all__'

# 마이페이지용 내 건의사항 list
class MySuggestionListSerializer(serializers.ModelSerializer):
    comments_cnt = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    category = serializers.SerializerMethodField(read_only=True) 
    
    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

    def get_comments_cnt(self, instance):
        return instance.comments_suggestion.count()
    
    def get_category(self, instance):
        return "건의사항"
    
    class Meta:
        model = Suggestion
        fields = [
            "id",
            "category",
            "title",
            "comments_cnt",
            "created_at"
        ]