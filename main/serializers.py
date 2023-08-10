from rest_framework import serializers
from django.db.models import Count
from .models import Ai, AiComment, Keyword, AiLike, AiRating
from user.models import Job
from django.shortcuts import get_object_or_404
from .paginations import AiCommentListPagination

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['keyword']

class CommentSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()


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
        return instance.created_at.strftime("%Y/%m/%d %H:%M")

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

class AiCommentListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        paginator = AiCommentListPagination()
        paginated_data = paginator.paginate_queryset(data, self.context['request'])
        serializers = CommentSerializer(paginated_data, many=True, context=self.context)
        return paginator.get_paginated_response(serializers.data).data


class DetailAiSerializer(serializers.ModelSerializer):
    is_liked = serializers.BooleanField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    avg_point = serializers.FloatField(read_only=True)
    my_rating_point = serializers.SerializerMethodField(read_only=True)
    rating_cnt = serializers.IntegerField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    keywords = serializers.SerializerMethodField(read_only=True)
    popular_job = serializers.SerializerMethodField(read_only=True)

    def get_my_rating_point(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            my_rating = AiRating.objects.filter(ai=instance,user=user).first()
            if my_rating == None:
                return 0
            return my_rating.rating
        return 0

    # def get_comments(self, instance):
    #     ai_comments = CommentSerializer(instance.comments_ai, many=True).data

    def get_comments(self, instance):
        ai_comments = instance.comments_ai.all()
        paginator = AiCommentListSerializer(context=self.context, child=CommentSerializer())
        return paginator.to_representation(ai_comments)

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
			"content",
            "url",
            "company",
            "applier",
            "keywords",
            "comments",
			"thumbnail",
            "popular_job",
            "is_liked",
			"likes_cnt",
            "my_rating_point",
			"avg_point",
			"rating_cnt",
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
        )
        list_serializer_class = AiCommentListSerializer

class AiSerializer(serializers.ModelSerializer):
    is_liked = serializers.BooleanField(read_only=True)
    likes_cnt = serializers.IntegerField(read_only=True)
    # avg_point = serializers.FloatField(read_only=True)
    rating_cnt = serializers.IntegerField(read_only=True) 
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
			# "avg_point",
			"rating_cnt",
        )
        read_only_fields = (
            "id",
			"title",
			"content",
            "keywords",
			"thumbnail",
        )
    
class TmpPasswordSerializer(serializers.Serializer):
    password =  serializers.CharField()
    