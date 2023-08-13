from django.urls import include, path
from rest_framework import routers

from .views import SuggestionViewSet, CommentViewSet, SuggestionCommentViewSet, CommentListViewSet

app_name = "suggestion"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("suggestions", SuggestionViewSet, basename="suggestions")

comment_router = routers.SimpleRouter(trailing_slash=False)
comment_router.register("comments", CommentViewSet, basename="comments")

suggestion_comment_router = routers.SimpleRouter(trailing_slash=False)
suggestion_comment_router.register("comments", SuggestionCommentViewSet, basename="comments")

comment_list_router = routers.SimpleRouter(trailing_slash=False)
comment_list_router.register("comments", CommentListViewSet, basename="comments-list")

urlpatterns = [
    path("", include(default_router.urls)),
    path("suggestions/moln/", include(comment_router.urls)), # 관리자 댓글 수정, 삭제 / 댓글 상세 보기
    path("suggestions/moln/<int:suggestion_id>/", include(suggestion_comment_router.urls)), # 관리자 댓글 작성, 건사 댓글 리스트
    path("suggestions/<int:suggestion_id>/", include(comment_list_router.urls)),
]