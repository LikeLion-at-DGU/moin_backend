from django.http import Http404

from rest_framework import viewsets, mixins, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

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
            likes_cnt=Count('likes'),
            # avg_point=Avg('rating_ai__rating'),
            rating_cnt=Count('rating_ai__rating'),
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
            likes_cnt=Count('likes'),
            avg_point=Avg('rating_ai__rating'),
            rating_cnt=Count('rating_ai__rating'),
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
