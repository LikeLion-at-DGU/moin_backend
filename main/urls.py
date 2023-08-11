from django.urls import path, include
from rest_framework import routers

from .views import AiViewSet, AiDetailViewSet, CommentViewSet, AiCommentViewSet, MyCommentViewSet

app_name = "main"

ai_router = routers.SimpleRouter()
ai_router.register("moin", AiViewSet, basename="moin")

ai_detail_router = routers.SimpleRouter()
ai_detail_router.register("moin/detail", AiDetailViewSet, basename="moin-detail")

ai_comment_router = routers.SimpleRouter()
ai_comment_router.register("comments", AiCommentViewSet, basename="comments") #리스트조회, 작성

comment_router = routers.SimpleRouter()
comment_router.register("comments", CommentViewSet, basename="comments") #수정, 삭제

ai_mycomment_router = routers.SimpleRouter()
ai_mycomment_router.register("mycomments", MyCommentViewSet, basename="mycomments")

urlpatterns = [
    path('', include(ai_router.urls)),
    path('', include(ai_detail_router.urls)),
    path('moin/detail/<str:ai_title>/',include(ai_comment_router.urls)),
    path('moin/detail/',include(comment_router.urls)),
    path('moin/detail/<str:ai_title>/',include(ai_mycomment_router.urls)),
]
