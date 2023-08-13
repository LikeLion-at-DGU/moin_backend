from django.urls import include, path
from rest_framework import routers

from .views import NotificationViewSet

app_name = "notice"

default_router = routers.SimpleRouter()
default_router.register("notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("", include(default_router.urls)),
]