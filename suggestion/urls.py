from django.urls import include, path
from rest_framework import routers

from .views import SuggestionViewSet, CommentViewSet, SuggestionCommentViewSet

app_name = "suggestion"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("suggestions", SuggestionViewSet, basename="suggestions")

comment_router = routers.SimpleRouter(trailing_slash=False)
comment_router.register("comments", CommentViewSet, basename="comments")

suggestion_comment_router = routers.SimpleRouter(trailing_slash=False)
suggestion_comment_router.register("comments", SuggestionCommentViewSet, basename="comments")

urlpatterns = [
    path("", include(default_router.urls)),
    path("suggestions/moln/", include(comment_router.urls)),   
    path("suggestions/moln/<int:suggestion_id>/", include(suggestion_comment_router.urls)),
]