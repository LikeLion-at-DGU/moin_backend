from django.urls import path, include
from .views import *
from rest_framework import routers

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

default_router = routers.SimpleRouter()
default_router.register("signup", SignUpViewSet, basename="signup")

# user_profile_router = routers.SimpleRouter()
# user_profile_router.register("mypage/profile", UserViewSet, basename="mypage-profile")

urlpatterns = [
    path('auth/', include(default_router.urls)),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    # 토큰
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # refresh token, access token 확인
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # refresh token 입력 시 새로운 access token
    #path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # profile
    #path('', include(user_profile_router.urls)),
    path('mypage/profile/', MyProfileViewSet.as_view(), name='mypage-profile'),
    path('users/<int:pk>/', OtherProfileViewSet.as_view(), name='user-profile'),
    path('users/<int:user_id>/tips/', OtherTipViewSet.as_view(), name='users-tips'),
    path('mypage/ai/likes/', MyLikedAiViewSet.as_view(), name='mypage-ai-likes'),
    path('mypage/community/likes/', MyLikedCommunityViewSet.as_view(), name='mypage-communiyt-likes'),
    path('mypage/posts/', MyPostViewSet.as_view(), name='mypage-posts'),
    path('mypage/community/comments/', MyCommunityCommentViewSet.as_view(), name='mypage-community-comments'),
    path('mypage/ai/comments/', MyAiCommentViewSet.as_view(), name='mypage-ai-comments'),
]