from django.urls import path, include
from rest_framework import routers

from .views import AiViewSet, AiDetailViewSet, AiInfoViewSet, CommentViewSet, AiCommentViewSet, MyCommentViewSet

app_name = "main"

ai_router = routers.SimpleRouter(trailing_slash=False)
ai_router.register("moin", AiViewSet, basename="moin")

ai_detail_router = routers.SimpleRouter(trailing_slash=False)
ai_detail_router.register("moin/detail", AiDetailViewSet, basename="moin-detail")

ai_info_router = routers.SimpleRouter(trailing_slash=False)
ai_info_router.register("info", AiInfoViewSet, basename="moin-detail-info")

ai_comment_router = routers.SimpleRouter(trailing_slash=False)
ai_comment_router.register("comments", AiCommentViewSet, basename="comments") #리스트조회, 작성

comment_router = routers.SimpleRouter(trailing_slash=False)
comment_router.register("comments", CommentViewSet, basename="comments") #수정, 삭제

ai_mycomment_router = routers.SimpleRouter(trailing_slash=False)
ai_mycomment_router.register("mycomments", MyCommentViewSet, basename="mycomments")

urlpatterns = [
    path('', include(ai_router.urls)),
    path('', include(ai_detail_router.urls)),
    path('moin/detail/<str:ai_title>/',include(ai_comment_router.urls)),
    path('moin/detail/<str:ai_title>/',include(ai_info_router.urls)),
    path('moin/detail/',include(comment_router.urls)),
    path('moin/detail/<str:ai_title>/',include(ai_mycomment_router.urls)),
]
