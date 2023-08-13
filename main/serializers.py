from rest_framework import serializers
from django.db.models import Count
from .models import Ai, AiComment, Keyword, AiLike, AiRating, AiInfo
from user.models import Job
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['keyword']

class CommentSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()


    def get_ai(self,instance): 
        return instance.ai.title
        
    def get_writer(self, instance):
        if instance.is_tmp:
            return "비회원"
        else:
            return instance.writer.nickname

    def get_created_at(self,instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")
    
    def get_updated_at(self,instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")

    class Meta:
        model = AiComment
        fields = (
            "id",
            "ai",
            "is_tmp",
            "writer",
            "content",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "ai",
            "is_tmp",
            "writer",
            "created_at",
            "updated_at",
        )

#임시유저의 ai 서비스 디테일 페이지
class DetailTmpUserAiSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    avg_point = serializers.FloatField(read_only=True)
    rating_cnt = serializers.IntegerField(read_only=True)
    my_rating_point = serializers.SerializerMethodField(read_only=True)
    keywords = serializers.SerializerMethodField(read_only=True)
    popular_job = serializers.SerializerMethodField(read_only=True)

    def get_my_rating_point(self, instance):
        return 0

    def get_is_liked(self, instance):
        return False
    
    def get_popular_job(self, instance):
        #상위 3개의 인기직군 주출
        top_jobs = AiLike.objects.filter(ai_id=instance).values('job').annotate(job_count=Count('job')).order_by('-job_count')[:3]
        top_jobs_ids = [job['job'] for job in top_jobs]

        popular_jobs = Job.objects.filter(id__in=top_jobs_ids)
        return [ pjob.name for pjob in popular_jobs]
    
    def get_keywords(self, instance):
        k_list = instance.keyword.all()
        return [k.name for k in k_list]

    class Meta:
        model = Ai
        fields = (
            "id",
			"title",
            "discription",
            "url",
            "company",
            "applier",
            "keywords",
			"thumbnail",
            "popular_job",
            "is_liked",
			"likes_cnt",
            "view_cnt",
            "my_rating_point",
			"avg_point",
			"rating_cnt",
        )
        read_only_fields = (
            "id",
			"title",
            "discription",
            "url",
            "company",
            "applier",
            "keywords",
			"thumbnail",
        )

#로그인 한 유저의 ai 서비스 디테일 페이지
class DetailUserAiSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    avg_point = serializers.FloatField(read_only=True)
    my_rating_point = serializers.SerializerMethodField(read_only=True)
    rating_cnt = serializers.IntegerField(read_only=True)
    keywords = serializers.SerializerMethodField(read_only=True)
    popular_job = serializers.SerializerMethodField(read_only=True)

    def get_my_rating_point(self, instance):
        user = self.context['request'].user
        my_rating = AiRating.objects.filter(ai=instance,user=user).first()
        if my_rating == None:
            return 0
        else:
            return my_rating.rating

    def get_is_liked(self, instance):
        user = self.context['request'].user
        return AiLike.objects.filter(ai=instance,user=user).exists()
        
    def get_popular_job(self, instance):
        #상위 3개의 인기직군 주출
        top_jobs = AiLike.objects.filter(ai_id=instance).values('job').annotate(job_count=Count('job')).order_by('-job_count')[:3]
        top_jobs_ids = [job['job'] for job in top_jobs]

        popular_jobs = Job.objects.filter(id__in=top_jobs_ids)
        return [ pjob.name for pjob in popular_jobs]
    
    def get_keywords(self, instance):
        k_list = instance.keyword.all()
        return [k.name for k in k_list]

    class Meta:
        model = Ai
        fields = (
            "id",
			"title",
            "discription",
            "url",
            "company",
            "applier",
            "keywords",
			"thumbnail",
            "popular_job",
            "is_liked",
			"likes_cnt",
            "view_cnt",
            "my_rating_point",
			"avg_point",
			"rating_cnt",
        )
        read_only_fields = (
            "id",
			"title",
            "discription",
            "url",
            "company",
            "applier",
            "keywords",
            "comments",
			"thumbnail",
        )

class AiSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    avg_point = serializers.FloatField(read_only=True)
    rating_cnt = serializers.IntegerField(read_only=True) 
    keywords = serializers.SerializerMethodField(read_only=True)

    def get_keywords(self, instance):
        k_list = instance.keyword.all()
        return [k.name for k in k_list]


    def get_is_liked(self, instance):
        User = get_user_model()
        user = self.context['request'].user if isinstance(self.context['request'].user, User) else None
        if user is not None:
            return AiLike.objects.filter(ai=instance,user=user).exists()
        else:
            return False
    
    class Meta:
        model = Ai
        fields = fields = (
            "id",
			"title",
            "discription",
            "keywords",
			"thumbnail",
            "is_liked",
			"likes_cnt",
			"avg_point",
			"rating_cnt",
        )
        read_only_fields = (
            "id",
			"title",
            "keywords",
			"thumbnail",
        )

class TmpPasswordSerializer(serializers.Serializer):
    password =  serializers.CharField()


class AiInfoSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField()

    def get_ai(self, instance):
        return instance.ai.title
    
    class Meta:
        model = AiInfo
        fields = (
            'ai',
            'introduce',
            'header_1',
            'content_1',
            'header_2',
            'content_2',
            'header_3',
            'content_3',
        )