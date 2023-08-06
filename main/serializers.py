from rest_framework import serializers
from .models import Ai, AiComment, Keyword

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['keyword']

class AiSerializer(serializers.ModelSerializer):
    # is_liked = serializers.BooleanField()
    likes_cnt = serializers.IntegerField()
    raing_point = serializers.FloatField()
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
        fields = (
            "id",
			"title",
			"content",
            "url",
            "company",
            "applier",
            "keywords",
            "comments",
			"thumbnail",
            # "popular_job",
			"likes_cnt",
			"raing_point",
			"rating_cnt",
            # "is_liked",
        )
        read_only_fields = (
            "id",
			"title",
			"content",
            "url",
            "company",
            "applier",
            "keywords",
            "comments",
			"thumbnail",
            # "popular_job",
			"likes_cnt",
			"raing_point",
			"rating_cnt",
            # "is_liked",
        )

class AiListSerializer(serializers.ModelSerializer):
    is_liked = serializers.BooleanField()
    likes_cnt = serializers.IntegerField()
    raing_point = serializers.FloatField()
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
            "keywords",
			"thumbnail",
            "is_liked",
			"likes_cnt",
			"raing_point",
			"rating_cnt",
        )
        read_only_fields = (
            "id",
			"title",
			"content",
            "keywords",
			"thumbnail",
            "is_liked",
			"likes_cnt",
			"raing_point",
			"rating_cnt",
        )

class CommentSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField(read_only=True)
    writer = serializers.SerializerMethodField(read_only=True)

    def get_ai(self, instance):
        return instance.ai.title
    
    def get_writer(self, instance):
        return instance.writer.username
    
    class Meta:
        model = AiComment
        fields = (
            "rating",
            "content",
            "ai",
            "writer",
        )
