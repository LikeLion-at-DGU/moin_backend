from django.urls import path, include
from rest_framework import routers
from . import views

from .views import CommunityViewSet, CommunityDetailViewSet, CommunityCommentViewSet, CommentViewSet, CommunityPostViewSet

app_name = "community"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("communities", CommunityViewSet, basename="")

community_detail_router = routers.SimpleRouter(trailing_slash=False)
community_detail_router.register("communities", CommunityDetailViewSet, basename="commuinties-detail")

community_post_router = routers.SimpleRouter(trailing_slash=False)
community_post_router.register("communities/posts", CommunityPostViewSet, basename="commuinties-post")

community_comment_router = routers.SimpleRouter(trailing_slash=False)
community_comment_router.register("comments", CommunityCommentViewSet, basename="comments") #리스트조회, 작성

comment_router = routers.SimpleRouter(trailing_slash=False)
comment_router.register("comments", CommentViewSet, basename="comments") #수정, 삭제

community_detail_action = {
    'get' : 'retrieve',
    'post' : 'like_action',
    'delete' : 'like_action'
}

urlpatterns = [
    path('communities/tips', views.CommunityViewSet.as_view({'get': 'list'}), {'category': 'tip'}, name='community-tips'),
    path('communities/commons', views.CommunityViewSet.as_view({'get': 'list'}), {'category': 'common'}, name='community-commons'),
    path('communities/qnas', views.CommunityViewSet.as_view({'get': 'list'}), {'category': 'qna'}, name='community-questions'),

    # 디테일페이지 url
    path('communities/tips/<int:pk>', views.CommunityDetailViewSet.as_view(community_detail_action), {'category': 'tip'}, name='community-tips-detail'),
    path('communities/commons/<int:pk>', views.CommunityDetailViewSet.as_view(community_detail_action), {'category': 'common'}, name='community-commons-detail'),
    path('communities/qnas/<int:pk>', views.CommunityDetailViewSet.as_view(community_detail_action), {'category': 'qna'}, name='community-questions-detail'),
    
    # 게시글 작성, 수정, 삭제
    path('', include(community_post_router.urls)),
    
    # 댓글 url
    path('communities/posts/<int:community_id>/',include(community_comment_router.urls)),
    path('communities/posts/',include(comment_router.urls)),
]