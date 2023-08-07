from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import JsonResponse

from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count, Q, Avg, Case, When ,BooleanField
from django.db.models.functions import Coalesce, Round
from django.db.models.expressions import Value
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Ai, AiLike, AiComment
from .serializers import AiSerializer, AiListSerializer
from .paginations import AiPagination

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
            return queryset.order_by('-rating_point')
        else:
            #기본 최신순
            return queryset.order_by('-updated_at')

#직군 검색 필터 커스텀
class Aifilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_param = request.query_params.get('filter')
        if filter_param:
            # 'filter' 쿼리 파라미터를 사용하여 'aijob__job__name' 필터링
            queryset = queryset.filter(Q(aijob__job__name=filter_param))

        return queryset

#Ai 뷰셋
class AiViewSet(viewsets.GenericViewSet,mixins.ListModelMixin):
    filter_backends = [AiOrderingFilter, Aifilter]
    filterset_fields = ['aijob__job__name']
    pagination_class = AiPagination
    serializer_class = AiListSerializer
    def get_queryset(self):
        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None

        queryset = Ai.objects.annotate(
            is_liked=Case(
                When(likes__user=user, then=True),
                default=False,
                output_field=BooleanField()
            ),
            likes_cnt=Count('likes'),
            rating_point=Round(Coalesce(Avg('comments_ai__rating'), Value(0.0))),
            rating_cnt=Count('comments_ai__rating'),
        )
        return queryset

    # def get_serializer_class(self):
    #     return AiListSerializer

class AiDetailViewSet(viewsets.GenericViewSet,mixins.RetrieveModelMixin):
    lookup_field = "title"
    serializer_class = AiSerializer
    def get_permissions(self):
        if self.action in ['like']:
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
            likes_cnt=Count('likes'),
            rating_point=Round(Coalesce(Avg('comments_ai__rating'), Value(0.0))),
            rating_cnt=Count('comments_ai__rating'),
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
