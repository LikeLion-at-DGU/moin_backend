from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Avg, OuterRef, Subquery
from .models import Ai, AiLike, AiComment
from .serializers import AiSerializer, AiListSerializer
from django.contrib.auth.decorators import login_required

# Create your views here.
class AiOrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        order_by = request.query_params.get(self.ordering_param)
        if order_by == 'popular':
            return queryset.order_by('-view_cnt')
        elif order_by == 'recent':
            return queryset.order_by('-updated_at')
        elif order_by == 'like':
            return queryset.order_by('-likes_cnt')
        elif order_by == 'rating':
            return queryset.order_by('-avg_rating')
        return super().filter_queryset(request, queryset, view)
    
class AiViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ai.objects.annotate(
        # is_liked
        likes_cnt=Count('likes'),
        avg_rating=Avg('comments_ai__rating'),
        rating_cnt=Count('comments_ai__rating'),
    )

    def get_serializer_class(self):
        if self.action == 'list':
            return AiListSerializer
        return AiSerializer
    
    filter_backends = [AiOrderingFilter,SearchFilter]
    search_fields = ['aijob__job__name']

    def retrieve_by_title(self, request, *args, **kwargs):
        title = kwargs.get('title')
        queryset = self.get_queryset()
        ai_instance = get_object_or_404(queryset, aijob__job__name=title)
        serializer = AiSerializer(ai_instance)
        return Response(serializer.data)
    
    # @login_required
    # def is_liked(request):
    #     user = request.user
    #     is_liked=Subquery(
    #     AiLikeTable.objects.filter(ai=OuterRef('pk'), user=user).values('id').annotate(
    #         is_liked=models.Value(True)
    #     ).values('is_liked')[:1]
