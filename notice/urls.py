from django.urls import include, path
from rest_framework import routers

from .views import NotificationViewSet

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("", include(default_router.urls)),
]