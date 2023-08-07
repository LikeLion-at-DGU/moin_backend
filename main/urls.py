from django.urls import path, include
from rest_framework import routers

from .views import AiViewSet, AiDetailViewSet

app_name = "main"

ai_router = routers.SimpleRouter()
ai_router.register("moin", AiViewSet, basename="moin")

ai_detail_router = routers.SimpleRouter()
ai_router.register("moin/detail", AiDetailViewSet, basename="moin/detail")

urlpatterns = [
    path('', include(ai_router.urls)),
    path('', include(ai_detail_router.urls)),
]
