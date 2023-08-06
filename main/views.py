from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Avg, Case, When, BooleanField
from django.db.models.functions import Coalesce
from django.db.models.expressions import Value
from .models import Ai, AiLike, AiComment
from .serializers import AiSerializer, AiListSerializer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Create your views here.
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
            return queryset.order_by('-updated_at')
        return super().filter_queryset(request, queryset, view)

class Aifilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_param = request.query_params.get('filter')

        if filter_param:
            # 'filter' 쿼리 파라미터를 사용하여 'aijob__job__name' 필터링
            queryset = queryset.filter(Q(aijob__job__name=filter_param))

        return queryset

class AiViewSet(viewsets.ReadOnlyModelViewSet):

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
            rating_point=Coalesce(Avg('comments_ai__rating'), Value(0.0)),
            # Coalesce : null일때 0 반환
            # Cast : 내림으로 정수 변환
            rating_cnt=Count('comments_ai__rating'),
        )
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return AiListSerializer
        return AiSerializer
    
    filter_backends = [AiOrderingFilter, Aifilter]
    filterset_fields = ['aijob__job__name']
