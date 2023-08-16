from rest_framework import viewsets, mixins, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from django.utils import timezone

from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib.auth import get_user_model

from .models import Community, CommunityComment, CommunityLike
from .serializers import *
from .paginations import CommunityCommentPagination, CommunityPagination
from .permissions import IsOwnerOrReadOnly

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
            return queryset.order_by('-created_at')
        
# 커뮤니티 목록 및 작성 뷰셋
class CommunityViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin
                ):
    filter_backends = [CommunityOrderingFilter, SearchFilter]
    search_fields = ['ai__title'] 
    pagination_class = CommunityPagination

    def get_serializer_class(self):
            queryset = self.get_queryset()
            category = queryset.values_list('category', flat=True).first()
            if category == 'tip':
                return TipListSerializer
            else:
                return CommonQnaListSerializer

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(writer = self.request.user)

    def get_queryset(self):
        category = self.kwargs.get('category')

        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None

        queryset = Community.objects.filter(category=category).annotate(
            likes_cnt=Count('likes_community', distinct=True)
        )
        return queryset
    
# 커뮤니티 디테일 뷰셋
class CommunityDetailViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin,
                            ):
    def get_serializer_class(self):
            queryset = self.get_queryset()
            category = queryset.values_list('category', flat=True).first()
            if category == 'common':
                return CommonDetailSerializer
            else:
                return QnaTipDetailSerializer
    
    def get_permissions(self):
        if self.action in ['like_action']:
            return [IsAuthenticated()]
        elif self.action in ['retrieve']:
            return [AllowAny()]
        else:
            return []
    
    def get_queryset(self):
        category = self.kwargs.get('category')

        User = get_user_model()
        user = self.request.user if isinstance(self.request.user, User) else None

        queryset = Community.objects.filter(category=category).annotate(
            likes_cnt=Count('likes_community', distinct=True)
        )
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_cnt += 1 
        instance.save()  

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='like')
    def like_action(self, request, *args, **kwargs):
        community = self.get_object()
        user = request.user
        community_like, created = CommunityLike.objects.get_or_create(community=community, user=user)

        if request.method == 'POST':
            community_like.save()
            return Response({"detail": "좋아요를 눌렀습니다."})
        
        elif request.method == 'DELETE':
            community_like.delete()
            return Response({"detail": "좋아요를 취소하였습니다."})

# 커뮤니티 게시물 작성, 수정, 삭제
class CommunityPostViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin
                            ):
    serializer_class = CommunityCreateUpdateSerializer

    queryset = Community.objects.all()

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        else:
            return [IsOwnerOrReadOnly()]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        
        # 업데이트 대상 필드를 수정하는 로직 추가
        if 'title' in data or 'content' in data:
            instance.title = data.get('title', instance.title)
            instance.content = data.get('content', instance.content)
            instance.updated_at = timezone.now()
            instance.save()
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_cnt += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# 커뮤니티 댓글 목록, 작성
class CommunityCommentViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    serializer_class = CommunityCommentSerializer
    pagination_class = CommunityCommentPagination
    filter_backends = [CommunityOrderingFilter]

    def get_permissions(self):
        if self.action in ['list']:
            return [AllowAny()]
        elif self.action in ['like','create']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        community_id = self.kwargs.get("community_id")
        community = get_object_or_404(Community, id=community_id)
        return CommunityComment.objects.filter(community=community)

    def create(self, request, *args, **kwargs):
        community_id = self.kwargs.get("community_id")
        community = get_object_or_404(Community, id=community_id)
        
        comment = CommunityComment.objects.create(
            community=community,
            content=request.data['content'],
            writer=request.user  # 로그인한 사용자를 작성자로 저장
        )

        serializer = CommunityCommentSerializer(comment)
        return Response(serializer.data)

# 커뮤니티 댓글 디테일, 수정, 삭제
class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = CommunityComment.objects.all()
    serializer_class=CommunityCommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ['retrieve','update','partial_update','destroy']:
            return [IsOwnerOrReadOnly()]
        return[]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)