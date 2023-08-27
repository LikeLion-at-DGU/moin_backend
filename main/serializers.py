from rest_framework import serializers
from django.db.models import Count
from .models import Ai, AiComment, Keyword, AiLike, AiRating, AiInfo, AiEngInfo
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

#Ai detail 시리얼라이저
class BaseDetailAiSerializer(serializers.ModelSerializer):
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
        top_jobs = AiLike.objects.filter(ai_id=instance).values('job').annotate(job_count=Count('job')).order_by('-job_count')[:3]
        top_jobs_ids = [job['job'] for job in top_jobs]

        popular_jobs = Job.objects.filter(id__in=top_jobs_ids)
        return [pjob.name for pjob in popular_jobs]
    
    def get_keywords(self, instance):
        k_list = instance.keyword.all()
        return [k.name for k in k_list]

    class Meta:
        model = Ai
        fields = (
            "id",
            "title",
            "description",
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
            "description",
            "url",
            "company",
            "applier",
            "keywords",
            "thumbnail",
        )

class DetailTmpUserAiSerializer(BaseDetailAiSerializer):
    class Meta(BaseDetailAiSerializer.Meta):
        fields = BaseDetailAiSerializer.Meta.fields

class DetailTmpUserAiEngSerializer(BaseDetailAiSerializer):
    eng_title = serializers.SerializerMethodField(read_only=True)
    eng_description = serializers.SerializerMethodField(read_only=True)

    def get_eng_title(self, instance):
        ai_eng_info = AiEngInfo.objects.filter(ai=instance).first()
        return ai_eng_info.eng_title if ai_eng_info else None

    def get_eng_description(self, instance):
        ai_eng_info = AiEngInfo.objects.filter(ai=instance).first()
        return ai_eng_info.eng_description if ai_eng_info else None
    
    class Meta(BaseDetailAiSerializer.Meta):
        fields = BaseDetailAiSerializer.Meta.fields + ('eng_title', 'eng_description', )

class DetailUserAiSerializer(BaseDetailAiSerializer):
    def get_my_rating_point(self, instance):
        user = self.context['request'].user
        my_rating = AiRating.objects.filter(ai=instance, user=user).first()
        if my_rating is None:
            return 0
        else:
            return my_rating.rating

    def get_is_liked(self, instance):
        user = self.context['request'].user
        return AiLike.objects.filter(ai=instance, user=user).exists()

    class Meta(BaseDetailAiSerializer.Meta):
        fields = BaseDetailAiSerializer.Meta.fields

class DetailUserAiEngSerializer(BaseDetailAiSerializer):
    eng_title = serializers.SerializerMethodField(read_only=True)
    eng_description = serializers.SerializerMethodField(read_only=True)

    def get_eng_title(self, instance):
        ai_eng_info = AiEngInfo.objects.filter(ai=instance).first()
        return ai_eng_info.eng_title if ai_eng_info else None

    def get_eng_description(self, instance):
        ai_eng_info = AiEngInfo.objects.filter(ai=instance).first()
        return ai_eng_info.eng_description if ai_eng_info else None

    def get_my_rating_point(self, instance):
        user = self.context['request'].user
        my_rating = AiRating.objects.filter(ai=instance, user=user).first()
        if my_rating is None:
            return 0
        else:
            return my_rating.rating

    def get_is_liked(self, instance):
        user = self.context['request'].user
        return AiLike.objects.filter(ai=instance, user=user).exists()

    class Meta(BaseDetailAiSerializer.Meta):
        fields = BaseDetailAiSerializer.Meta.fields + ('eng_title', 'eng_description', )

#Ai list 시리얼라이저
class BaseAiSerializer(serializers.ModelSerializer):
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
        fields = (
            "id",
            "title",
            "description",
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

class AiSerializer(BaseAiSerializer):
    class Meta(BaseAiSerializer.Meta):
        pass

class AiEngSerializer(BaseAiSerializer):
    eng_title = serializers.SerializerMethodField(read_only=True)
    eng_description = serializers.SerializerMethodField(read_only=True)

    def get_eng_title(self, instance):
        ai_eng_info = AiEngInfo.objects.filter(ai=instance).first()
        return ai_eng_info.eng_title if ai_eng_info else None

    def get_eng_description(self, instance):
        ai_eng_info = AiEngInfo.objects.filter(ai=instance).first()
        return ai_eng_info.eng_description if ai_eng_info else None

    class Meta(BaseAiSerializer.Meta):
        fields = BaseAiSerializer.Meta.fields + ("eng_title", "eng_description")

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

class AiEngInfoSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField()

    def get_ai(self, instance):
        return instance.ai.title
    
    class Meta:
        model = AiEngInfo
        fields = (
            'ai',
            'eng_title',
            'introduce',
            'header_1',
            'content_1',
            'header_2',
            'content_2',
            'header_3',
            'content_3',
        )

# ai 전체 목록만 보내주는 시리얼라이저
class AllAiListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ai
        fields = ['title']

# 마이페이지 내 댓글 관련
class MyAiCommentListSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    updated_at = serializers.SerializerMethodField(read_only=True)
    category = serializers.SerializerMethodField(read_only=True) 
    
    def get_ai(self, instance):
        return instance.ai.title

    def get_created_at(self, instance):
        return instance.created_at.strftime("%Y/%m/%d %H:%M")
    
    def get_updated_at(self, instance):
        return instance.updated_at.strftime("%Y/%m/%d %H:%M")
    
    def get_category(self, instance):
        return "ai"
    
    class Meta:
        model = AiComment
        fields = [
            "id",
            "ai",
            "category",
            "content",
            "created_at",
            "updated_at"
        ]

class MyLikeAiSerializer(serializers.ModelSerializer):
    likes_cnt = serializers.SerializerMethodField(read_only=True)
    avg_point = serializers.SerializerMethodField(read_only=True)
    rating_cnt = serializers.SerializerMethodField(read_only=True) 
    keywords = serializers.SerializerMethodField(read_only=True)

    def get_keywords(self, instance):
        k_list = instance.keyword.all()
        return [k.name for k in k_list]
    
    def get_likes_cnt(self, instance):
        return instance.likes_cnt  
    
    def get_avg_point(self, instance):
        return instance.avg_point

    def get_rating_cnt(self, instance):
        return instance.rating_cnt  

    class Meta:
        model = Ai
        fields = (
            "id",
			"title",
            "description",
            "keywords",
			"thumbnail",
			"likes_cnt",
			"avg_point",
			"rating_cnt",
        )


##영어 호출 임시