from django.urls import path, include
from .views import SignUpViewSet, LoginViewSet
from rest_framework import routers

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

default_router = routers.SimpleRouter()
default_router.register("signup", SignUpViewSet, basename="signup")

login_router = routers.SimpleRouter()
login_router.register("login", LoginViewSet, basename="login")

urlpatterns = [
    path('', include(default_router.urls)),
    path('', include(login_router.urls)),
    # 토큰
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # refresh token, access token 확인
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # refresh token 입력 시 새로운 access token
    #path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]