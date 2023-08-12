from django.urls import path, include
from rest_framework import routers

from .views import CommunityViewSet, CommunityCreateViewSet, CommunityDetailViewSet, CommentViewSet, CommunityCommentViewSet

app_name = "community"

community_list_router = routers.SimpleRouter(trailing_slash=False)
community_list_router.register("communities", CommunityViewSet, basename="communities")

community_create_router = routers.SimpleRouter(trailing_slash=False)
community_create_router.register("communities/posts", CommunityCreateViewSet, basename="communities-create")

community_detail_router = routers.SimpleRouter(trailing_slash=False)
community_detail_router.register("communities/posts", CommunityDetailViewSet, basename="commuinties-detail")

comment_router = routers.SimpleRouter(trailing_slash=False)
comment_router.register("comments", CommentViewSet, basename="comments") # 수정, 삭제

community_comment_router = routers.SimpleRouter(trailing_slash=False)
community_comment_router.register("comments", CommunityCommentViewSet, basename="comments") # 리스트 조회, 작성

urlpatterns = [    
    path('', include(community_list_router.urls)),
    path('', include(community_create_router.urls)),
    path('', include(community_detail_router.urls)),
    path('communities/posts/', include(comment_router.urls)),
    path('communities/posts/<int:community_id>/', include(community_comment_router.urls)),
]