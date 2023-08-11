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

from .models import Community, CommunityImage, CommunityComment, CommunityLike
from .serializers import *
from .paginations import CommunityCommentPagination, CommunityPagination
from .permissions import *

# Create your views here.
# 정렬
class CommunityOrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        order_by = request.query_params.get(self.ordering_param)
        if order_by == 'popular':
            return queryset.order_by('-view_cnt')
        elif order_by == 'like':
            return queryset.order_by('-likes_cnt')
        else:
            #기본 최신순
            return queryset.order_by('-updated_at')
        
# 커뮤니티 뷰셋
class CommunityViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    filter_backends = [CommunityOrderingFilter]
    pagination_class = CommunityPagination

    def get_serializer_class(self):
        if self.action == "list":
            return CommunitySerializer
        else:
            return CommunityCreateSerailizer
        
    def perform_create(self, serializer):
        serializer.save(writer = self.request.user)

    def get_queryset(self):
        category = self.kwargs.get('category')

        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None
        
        queryset = Community.objects.filter(category=category).annotate(
            is_liked=Case(
                When(likes_community__user=user, then=True),
                default=False,
                output_field=BooleanField()
            ),
            likes_cnt=Count('likes_community', distinct=True)
        )
    
        return queryset
    
    
    
# 커뮤니티 디테일 뷰셋
class CommunityDetailViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin
                            ):
    
    def get_serializer_class(self):
        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None
        if user != None:
            return CommunityUserDetailSerializer
        else:
            return CommunityTmpDetailSerializer
        
    def get_permissions(self):
        if self.action in ['like']:
            return [IsAuthenticated()]
        return[]
    
    def get_queryset(self):
        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None

        queryset = Community.objects.annotate(
            is_liked=Case(
                When(likes_community__user=user, then=True),
                default=False,
                output_field=BooleanField()
            ),
            likes_cnt=Count('likes_community', distinct=True)
        )
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_cnt += 1 
        instance.save()  

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(methods=['GET'], detail=True, url_path='like')
    def like_action(self, request, *args, **kwargs):
        community = self.get_object()
        user = request.user
        community_like, created = CommunityLike.objects.get_or_create(community=community, user=user)

        if created:
            #좋아요가 없었던 경우
            community_like.save()
            return Response({"detail": "좋아요를 누르셨습니다."})
        else:
            #좋아요가 있었던 경우
            community_like.delete()
            return Response({"detail": "좋아요를 취소하셨습니다."})