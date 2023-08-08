from rest_framework import serializers
from django.db.models import Count
from .models import Ai, AiComment, AiTempComment, Keyword, AiLike
from user.models import Job

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['keyword']

class DetailAiSerializer(serializers.ModelSerializer):
    is_liked = serializers.BooleanField()
    likes_cnt = serializers.IntegerField()
    avg_point = serializers.IntegerField()
    my_rating_point = serializers.SerializerMethodField(read_only=True)
    rating_cnt = serializers.IntegerField()
    comments = serializers.SerializerMethodField(read_only=True)
    keywords = serializers.SerializerMethodField(read_only=True)
    popular_job = serializers.SerializerMethodField(read_only=True)


    def get_my_rating_point(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            my_rating = AiComment.objects.filter(ai=instance, writer_id=user).first().rating
            if my_rating == None:
                return 0
            return my_rating
        return 0

    
    def get_popular_job(self, instance):
        #상위 3개의 인기직군 주출
        top_jobs = AiLike.objects.filter(ai_id=instance).values('job').annotate(job_count=Count('job')).order_by('-job_count')[:3]
        top_jobs_ids = [job['job'] for job in top_jobs]

        popular_jobs = Job.objects.filter(id__in=top_jobs_ids)
        return [ pjob.name for pjob in popular_jobs]

    def get_comments(self, instance):
        ai_comments = ListCommentSerializer(instance.comments_ai, many=True).data
        temp_comments = ListCommentSerializer(instance.temp_comments_ai, many=True).data
        all_comments = ai_comments + temp_comments

        sorted_comments = sorted(all_comments, key=lambda comment: comment['created_at'])
        return sorted_comments
    
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
            # "popular_job",
			"likes_cnt",
            "my_rating_point",
			"avg_point",
			"rating_cnt",
            "is_liked",
        )

class AiSerializer(serializers.ModelSerializer):
    is_liked = serializers.BooleanField()
    likes_cnt = serializers.IntegerField()
    avg_point = serializers.FloatField()
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
			"avg_point",
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
			"avg_point",
			"rating_cnt",
        )

class ListCommentSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField()  
    writer = serializers.SerializerMethodField()

    def get_ai(self, instance):
        ai = instance.ai
        return ai.title

    def get_writer(self, instance):
        if isinstance(instance, AiComment):
            return instance.writer.nickname  # 일반 유저의 경우 username 반환
        return "비회원"

    def get_is_temp(self, instance):
        return isinstance(instance, AiTempComment) #일반유저 false

    def to_representation(self, instance): #댓글 모델에 따라 다른 Meta.model 사용
        if isinstance(instance, AiComment):
            self.Meta.model = AiComment
        else:
            self.Meta.model = AiTempComment
        return super().to_representation(instance)
    
    class Meta:
        model = None  # to_representaion에서 설정
        fields = (
            "ai",
            "writer",
            "content",
            "created_at",
        )

class CommentSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField()  
    writer = serializers.SerializerMethodField()  
    
    def get_ai(self, instance):
        ai = instance.ai
        return ai.title

    def get_writer(self, instance):
        return instance.writer.nickname  # 일반 유저의 경우 username 반환

    # def get_is_temp(self, instance):
    #     return isinstance(instance, AiTempComment) #일반유저 false

    # def to_representation(self, instance): #댓글 모델에 따라 다른 Meta.model 사용
    #     if isinstance(instance, AiComment):
    #         self.Meta.model = AiComment
    #     else:
    #         self.Meta.model = AiTempComment
    #     return super().to_representation(instance)
    
    class Meta:
        model = AiComment  # to_representaion에서 설정
        fields = (
            "ai",
            "writer",
            "rating",
            "content",
            "created_at",
        )

class TempCommentSerializer(serializers.ModelSerializer):
    ai = serializers.SerializerMethodField()  
    writer = serializers.SerializerMethodField()  
    
    def get_ai(self, instance):
        ai = instance.ai
        return ai.title
    
    def get_writer(self, instance):
        return "비회원"
    
    class Meta:
        model = AiTempComment  # to_representaion에서 설정
        fields = (
            "ai",
            "writer",
            "tmp_password",
            "content",
            "created_at",
        )