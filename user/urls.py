from django.urls import path, include
from .oauth import *
from .views import *
from rest_framework import routers

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("signup", SignUpViewSet, basename="signup")

social_user_apply = routers.SimpleRouter(trailing_slash=False)
social_user_apply.register("apply", SocialUserApplyViewSet, basename="apply")

# user_profile_router = routers.SimpleRouter()
# user_profile_router.register("mypage/profile", UserViewSet, basename="mypage-profile")

urlpatterns = [
    path('auth/', include(default_router.urls)),
    path('auth/login', LoginAPIView.as_view(), name='login'),
    path('auth/password/change', CustomPasswordChangeView.as_view(), name='rest_password_change'),
    path('auth/password-reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/password-reset', PasswordResetRequestView.as_view(), name='password_reset'),
    # 토큰
    path('auth/token', TokenObtainPairView.as_view(), name='token_obtain_pair'), # refresh token, access token 확인
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'), # refresh token 입력 시 새로운 access token
    #path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    #구글
    path('auth/google/login/', google_login, name='google_login'),
    path('auth/google/login/callback/', google_callback, name='google_callback'),
    path('auth/google/login/finish/', GoogleLogin.as_view(), name='google_login_todjango'),

    #카카오
    path('auth/kakao/login/', kakao_login, name='kakao_login'),
    path('auth/kakao/login/callback/', kakao_callback, name='kakao_callback'),
    path('auth/kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),

    # 소셜 후 유저 등록
    path('auth/social/', include(social_user_apply.urls)),

    # 작성자 본인 확인
    path('users/check', CheckWriterAPIView.as_view(), name='check-writer'),

    # profile
    #path('', include(user_profile_router.urls)),
    path('mypage/profile', MyProfileViewSet.as_view(), name='mypage-profile'),
    path('users/<int:pk>', OtherProfileViewSet.as_view(), name='user-profile'),
    path('users/<int:user_id>/tips', OtherTipViewSet.as_view(), name='users-tips'),

    ## 자기 프로필 관련 url
    path('mypage/ai/likes', MyLikedAiViewSet.as_view(), name='mypage-ai-likes'), # 좋아요 한 서비스
    path('mypage/community/likes', MyLikedCommunityViewSet.as_view(), name='mypage-communiyt-likes'), # 좋아요 한 게시물
    path('mypage/posts', MyAllPostViewSet.as_view(), name='mypage-posts'), # 작성한 전체 게시물
    path('mypage/posts/suggestions', MySuggestionViewSet.as_view(), name='mypost-suggestion'), # 작성한 건의사항
    path('mypage/posts/tips', MyPostTipViewSet.as_view(), name='mypost-tip'), # 작성한 qna
    path('mypage/posts/commons', MyPostCommonViewSet.as_view(), name='mypost-common'), # 작성한 commons
    path('mypage/posts/qnas', MyPostQnaViewSet.as_view(), name='mypost-qna'), # 작성한 tips
    path('mypage/comments', MyAllCommentViewSet.as_view(), name='mypage-community-comments'), # 작성한 전체 댓글
    # path('mypage/comments/ai', ) # 작성한 ai 서비스 후기
    path('mypage/comments/qnas', MyQnaCommentViewSet.as_view(), name='mycomment-qna'), # 작성한 qna 댓글
    path('mypage/comments/commons', MyCommonCommentViewSet.as_view(), name='mycomment-common'), # 작성한 commons 댓글
    path('mypage/comments/tips', MyTipCommentViewSet.as_view(), name='mycomment-tip'), # 작성한 tips 댓글
    path('mypage/comments/ai', MyAiCommentViewSet.as_view(), name='mypage-ai-comments'),
]