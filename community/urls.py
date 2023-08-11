from django.urls import path, include
from rest_framework import routers

from .views import CommunityViewSet, CommunityDetailViewSet

app_name = "community"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("communities", CommunityViewSet, basename="communities")

community_detail_router = routers.SimpleRouter(trailing_slash=False)
community_detail_router.register("communities", CommunityDetailViewSet, basename="commuinties-detail")

urlpatterns = [
    path('', include(default_router.urls)),
    path('communities/tips/', CommunityViewSet.as_view({'get': 'list'}), {'category': 'tip'}, name='community-list-tips'),
    path('communities/commons/', CommunityViewSet.as_view({'get': 'list'}), {'category': 'common'}, name='community-list-commons'),
    path('communities/qnas/', CommunityViewSet.as_view({'get': 'list'}), {'category': 'qna'}, name='community-list-qnas'),
    path('', include(community_detail_router.urls)),
]