from django.urls import path, include
from rest_framework import routers

from .views import AiViewSet

app_name = "main"

ai_router = routers.SimpleRouter()
ai_router.register("moin", AiViewSet, basename="moin")

urlpatterns = [
    path('', include(ai_router.urls)),
]

# ai_list = AiViewSet.as_view({
#     'get' : 'list',
# })
# ai_detail = AiViewSet.as_view({
#     'get' : 'retrieve',
# })
# urlpatterns = [
#     path('moin', ai_list, name='ai-list'),
#     path('moin/detail/<str:title>/', ai_detail, name='ai-detail'),
# ]

#액션