from django.urls import path, include
from rest_framework import routers
from . import views

from .views import CommunityViewSet, CommunityDetailViewSet

app_name = "community"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("communities", CommunityViewSet, basename="")

community_detail_router = routers.SimpleRouter(trailing_slash=False)
community_detail_router.register("communities", CommunityDetailViewSet, basename="commuinties-detail")

urlpatterns = [
    path('', include(default_router.urls)),
    path('communities/tips/', views.CommunityViewSet.as_view({'get': 'list'}), {'category': 'tip'}, name='community-tips'),
    path('communities/commons/', views.CommunityViewSet.as_view({'get': 'list'}), {'category': 'common'}, name='community-commons'),
    path('communities/qnas/', views.CommunityViewSet.as_view({'get': 'list'}), {'category': 'qna'}, name='community-qnas'),
    path('', include(community_detail_router.urls)),
]