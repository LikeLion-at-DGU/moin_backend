from django.urls import path, include
from .views import SignUpViewSet, LoginAPIView, PasswordResetRequestView, PasswordResetConfirmView
from .oauth import google_login, google_callback, GoogleLogin
from rest_framework import routers

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

default_router = routers.SimpleRouter()
default_router.register("signup", SignUpViewSet, basename="signup")

urlpatterns = [
    path('', include(default_router.urls)),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    # 토큰
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # refresh token, access token 확인
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # refresh token 입력 시 새로운 access token
    #path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    #구글
    path('google/login', google_login, name='google_login'),
    path('google/login/callback/', google_callback, name='google_callback'),
    path('google/login/finish/', GoogleLogin.as_view(), name='google_login_todjango'),
]