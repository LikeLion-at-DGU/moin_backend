from rest_framework import serializers
from .models import Ai, AiComment, Keyword

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['keyword']

class AiSerializer(serializers.ModelSerializer):
    # is_liked = serializers.BooleanField()
    likes_cnt = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    rating_cnt = serializers.IntegerField()
    comments = serializers.SerializerMethodField(read_only=True)
    keywords = serializers.SerializerMethodField(read_only=True)

    def get_comments(self, instance):
        serializers = CommentSerializer(instance.comments_ai, many=True)
        return serializers.data
    
    def get_keywords(self, instance):
        k_list = instance.keyword.all()
        return [k.name for k in k_list]

    class Meta:
        model = Ai
        fields = "__all__"
        read_only_fields = (
            "id",
			"title",
			"content",
			"thumbnail",
			"like_cnt",
			"avg_rating",
			"rating_cnt",
        )

class AiListSerializer(serializers.ModelSerializer):
    # is_liked = serializers.BooleanField()
    likes_cnt = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    rating_cnt = serializers.IntegerField() 
    keywords = serializers.SerializerMethodField(read_only=True)

    def get_keywords(self, instance):
        k_list = instance.keyword.all()
        return [k.name for k in k_list]

    class Meta:
        model = Ai
        fields = fields = (
            "id",
			"title",
			"content",
			"thumbnail",
			"likes_cnt",
			"avg_rating",
			"rating_cnt",
            "keywords"
        )
        read_only_fields = (
            "id",
			"title",
			"content",
			"thumbnail",
			"likes_cnt",
			"avg_rating",
			"rating_cnt",
        )

class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AiComment
        fields = '__all__'
        read_only_fields = ['ai']

class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AiComment
        fields = '__all__'
