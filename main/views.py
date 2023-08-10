from django.http import Http404

from rest_framework import viewsets, mixins, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter

from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count, Q, Avg, Case, When ,BooleanField
from django.db.models.functions import Coalesce, Round
from django.db.models.expressions import Value
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Ai, AiLike, AiComment
from .serializers import *
from .paginations import AiPagination
from .permissions import *

# Create your views here.

# 정렬 필터 커스텀
class AiOrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        order_by = request.query_params.get(self.ordering_param)
        if order_by == 'popular':
            return queryset.order_by('-view_cnt')
        elif order_by == 'like':
            return queryset.order_by('-likes_cnt')
        elif order_by == 'rating':
            return queryset.order_by('-avg_point')
        else:
            #기본 최신순
            return queryset.order_by('-updated_at')

#직군 검색 필터 커스텀
class Aifilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_keyword_param = request.query_params.getlist('keyword')
        filter_job_param = request.query_params.getlist('job')
        if filter_job_param:
            #인기직군 3개를 기준으로 검색
            popular_jobs = AiLike.objects.filter(job__name=filter_job_param).values('ai').annotate(job_count=Count('job')).order_by('-job_count')
            ai_ids_with_popular_jobs = [entry['ai'] for entry in popular_jobs]
            queryset = queryset.filter(id__in=ai_ids_with_popular_jobs)

        if filter_keyword_param:
            # 키워드를 사용하여 검색
            queryset = queryset.filter(keywords__name=filter_keyword_param)

        return queryset

#Ai 뷰셋
class AiViewSet(viewsets.GenericViewSet,mixins.ListModelMixin):
    filter_backends = [AiOrderingFilter, Aifilter, SearchFilter]
    search_fields = ['title', 'keywords__name', 'discription', 'content', 'company']  
    filterset_fields = ['aijob__job__name']
    pagination_class = AiPagination
    serializer_class = AiSerializer

    def get_queryset(self):
        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None
        
        queryset = Ai.objects.annotate(
            is_liked=Case(
                When(likes__user=user, then=True),
                default=False,
                output_field=BooleanField()
            ),
            likes_cnt=Count('likes',distinct=True),
            # avg_point=Avg('rating_ai__rating'),
            rating_cnt=Count('rating_ai__rating', distinct=True),
        )
        return queryset

    # def get_serializer_class(self):
    #     return AiListSerializer

class AiDetailViewSet(viewsets.GenericViewSet,mixins.RetrieveModelMixin):
    lookup_field = "title"

    def get_serializer_class(self):
        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None
        if user != None:
            return DetailUserAiSerializer
        else:
            return DetailTmpUserAiSerializer

    def get_permissions(self):
        if self.action in ['like','rate']:
            return [IsAuthenticated()]
        return[]
    
    
    def get_queryset(self):
        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None

        queryset = Ai.objects.annotate(
            is_liked=Case(
                When(likes__user=user, then=True),
                default=False,
                output_field=BooleanField()
            ),
            likes_cnt=Count('likes',distinct=True),
            avg_point=Avg('rating_ai__rating'),
            rating_cnt=Count('rating_ai__rating', distinct=True),
        )
        return queryset
    
    @action(methods=['GET'], detail=True, url_path='like')
    def like_action(self, request, *args, **kwargs):
        ai = self.get_object()
        user = request.user
        ai_like, created = AiLike.objects.get_or_create(ai=ai, user=user)

        if created:
            #좋아요가 없었던 경우/직업 저장
            ai_like.job = user.job
            ai_like.save()
            return redirect('..')
        else:
            #좋아요가 있었던 경우
            ai_like.delete()
            return redirect('..')
    
    @action(methods=['PATCH'], detail=True, url_path='rate', )
    def rate_action(self, request, *args, **kwargs):
        ai = self.get_object()
        user = request.user
        rating = AiRating.objects.get(ai=ai,user=user)
        rating.rating = request.data['rating']
        rating.save()
        return Response({"detail": "평점이 변경되었습니다.", "rating" : request.data['rating']}, status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(viewsets.GenericViewSet,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin):
    serializer_class=CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ['list','partial_update','destroy']:
            return [IsOwnerOrReadOnly()]
        return[]
    
    def get_queryset(self):
        title = self.kwargs.get("ai_title")
        ai_id = get_object_or_404(Ai, title=title).id
        return AiComment.objects.filter(ai_id=ai_id)

    def destroy(self, request, *args, **kwargs):
        comment_id = self.kwargs.get("pk")
        try:
            instance = AiComment.objects.get(id=comment_id)
        except AiComment.DoesNotExist:
            raise Http404
        
        instance.delete()
        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
    
    def create(self, request, *args, **kwargs):
        title = self.kwargs.get("ai_title")
        ai = get_object_or_404(Ai, title=title)
        if request.user.is_authenticated:
            comment = AiComment.objects.create(
                ai=ai,
                content=request.data['content'],
                writer=request.user  # 로그인한 사용자를 작성자로 저장
            )
        else:
            if request.data['password']:
                comment = AiComment.objects.create(
                    ai=ai,
                    is_tmp=True,
                    tmp_password=request.data['password'],
                    content=request.data['content'],
                )
            else:
                return Response(status=400)

        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    @action(methods=['POST'], detail=True, url_path='delete_tmp')
    def delete_action(self, request, *args, **kwargs):
        serializer = TmpPasswordSerializer(data=request.data)
        comment_id = self.kwargs.get("pk")
        instance = AiComment.objects.get(id=comment_id)
        if serializer.is_valid():
            if serializer.validated_data['password'] == instance.tmp_password:
                self.perform_destroy(instance)
                return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"detail": "올바르지 않은 비밀번호입니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
