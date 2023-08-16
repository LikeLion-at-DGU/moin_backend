from rest_framework import viewsets, status, mixins, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import EmailMessage
from dj_rest_auth.views import PasswordChangeView

from .serializers import UserLoginSerializer, UserRegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, CustomPasswordChangeSerializer, CheckWriterSerializer, SocialUserSerializer
from .models import User, Job
from community.models import Community, CommunityComment
from main.models import AiComment
from suggestion.models import Suggestion

class SignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def create(self, request):
        password = request.data.get('password')

        job = request.data['job']  # job 가져오기
        user_data = {
            'email' : request.data['email'],
            'nickname' : request.data['nickname'],
            'description' : request.data['description'],
            'job' : Job.objects.get(name=job)
        }
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        res = Response(
            {
                "message": "회원가입 성공!"
            },
            status=status.HTTP_200_OK,
            )
        return res

class LoginAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.get(email=email)
        user = authenticate(request, email=email,password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            login(request, user)
            res = Response(
                {
                    "user": {
                        'nickname': user.nickname,
                        'email': user.email,
                        'description' : user.description,
                        'job': user.job.name,
                        'password' : user.password
                    },
                    "message": "로그인 성공!",
                    "token": {
                        "access": access_token,
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_200_OK,
                )
            return res
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CustomPasswordChangeView(PasswordChangeView):
    serializer_class = CustomPasswordChangeSerializer

class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer
    
    def get_frontend_url(self):
        if self.request.META['HTTP_HOST'] in ['localhost:8000','127.0.0.1:8000']: #로컬환경 테스트용
            return 'localhost:8000'
        else:
            current_site = get_current_site(self.request)
            return f"https://{current_site.domain}"
    
    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': '유저를 찾을 수 없음'}, status=status.HTTP_404_NOT_FOUND)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        #비밀번호 초기화 url 생성
        reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        reset_url = f"{self.get_frontend_url()}{reset_url}"

        email_message = EmailMessage('MO:IN 비밀번호 초기화 주소', reset_url, to=[email])
        email_message.send()

        return Response({'detail': '비밀번호 재설정 메일 발송완료.'})

class PasswordResetConfirmView(generics.CreateAPIView):
    serializer_class = PasswordResetConfirmSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb64 = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')
        password = serializer.validated_data['password']
        confirm = serializer.validated_data['confirm']

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': '주소가 유효하지 않음'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):

            if password != confirm:
                return Response({'detail': '비밀번호 불일치'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()
            return Response({'detail': '비밀번호 재설정 완료'})
        
        return Response({'detail': '주소가 유효하지 않음'}, status=status.HTTP_400_BAD_REQUEST)
    
class SocialUserApplyViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin
                            ):
    serializer_class = SocialUserSerializer


# 작성자 본인 확인 api
class CheckWriterAPIView(APIView):
    def get(self, request, *args, **kwargs):
        type = request.query_params.get('type')  # 요청에서 객체 유형 가져오기
        id = request.query_params.get('id')  # 요청에서 객체 ID 가져오기

        if type == 'community':
            try:
                obj = Community.objects.get(id=id)
            except Community.DoesNotExist:
                return Response({'error': '없는 커뮤니티 게시물입니다. id값을 다시 확인해보세요!'}, status=status.HTTP_404_NOT_FOUND)
        elif type == 'community_comment':
            try:
                obj = CommunityComment.objects.get(id=id)
            except CommunityComment.DoesNotExist:
                return Response({'error': '없는 커뮤니티 댓글입니다. id값을 다시 확인해보세요!'}, status=status.HTTP_404_NOT_FOUND)
        elif type == 'ai_comment':
            try:
                obj = AiComment.objects.get(id=id)
            except AiComment.DoesNotExist:
                return Response({'error': '없는 ai 댓글입니다. id값을 다시 확인해보세요!'}, status=status.HTTP_404_NOT_FOUND)
        elif type == 'suggestion':
            try:
                obj = Suggestion.objects.get(id=id)
            except Suggestion.DoesNotExist:
                return Response({'error': '없는 건의사항입니다. id값을 다시 확인해보세요!'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Invalid object type'}, status=status.HTTP_400_BAD_REQUEST)

        # 작성자와 로그인한 유저 비교
        is_writer = obj.writer == request.user

        serializer = CheckWriterSerializer({'is_writer': is_writer})
        return Response(serializer.data, status=status.HTTP_200_OK)


#####################################################################################################
# Profile 기능 구현
from rest_framework import viewsets
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from .models import User
from rest_framework.decorators import action
from .serializers import UserSerializer
from django.shortcuts import redirect, get_object_or_404
from itertools import chain
from operator import attrgetter

from django.db.models import Count
from community.models import Community, CommunityComment, CommunityLike
from community.serializers import MyCommunityCommentSerializer, MyPostCommunityListSerializer, TipListSerializer, CommunitySerializer, CommunityCommentSerializer, MyAllPostSerializer

from suggestion.serializers import MySuggestionListSerializer

from main.serializers import MyAiCommentListSerializer, AiSerializer
from main.models import Ai, AiComment, AiLike

from .paginations import UserPagination, MyLikeTipPagination
    
# 타유저 프로필 조회    
class OtherProfileViewSet(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    http_method_names = ['get']
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# 타유저의 꿀팁 작성 목록 조회
class OtherTipViewSet(generics.ListAPIView):
    serializer_class = TipListSerializer
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        # 타유저가 작성한 커뮤니티 글 중 category='tip'인 목록만 가져옴
        return Community.objects.filter(writer=self.kwargs['user_id'], category='tip')
    
# 내 프로필 조회, 수정
class MyProfileViewSet(generics.RetrieveUpdateAPIView): # 조회랑 수정만 할 거니까
    serializer_class = UserSerializer
    http_method_names = ['get','put', 'patch']
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            User.objects.select_related("job"), # job 모델 정보도 가져옴
            id=self.request.user.id
        )

# 내가 좋아요 한 AI 목록 조회 - 페이지네이션 12
class MyLikedAiViewSet(generics.ListAPIView):
    serializer_class = AiSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MyLikeTipPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        liked_aids = AiLike.objects.filter(user=user).values_list('ai_id', flat=True)
        return Ai.objects.filter(id__in=liked_aids)
    
# 내가 좋아요 한 커뮤니티 게시물 목록 조회
class MyLikedCommunityViewSet(generics.ListAPIView):
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        liked_communities = CommunityLike.objects.filter(user=user).values_list('community_id', flat=True)
        return Community.objects.filter(id__in=liked_communities)
    
# 내가 작성한 게시물
# 내가 작성한 전체 게시물 목록 조회(커뮤+건의)
class MyAllPostViewSet(generics.ListAPIView):
    serializer_class = MyAllPostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        communities = Community.objects.filter(writer=user)
        suggestions = Suggestion.objects.filter(writer=user)
        combined_posts = sorted(chain(communities, suggestions), key=attrgetter('created_at'), reverse=True)
        return combined_posts
    
# 내가 작성한 tip 게시물 목록 조회
class MyPostTipViewSet(generics.ListAPIView):
    serializer_class = MyPostCommunityListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        category = 'tip'

        queryset = Community.objects.filter(writer=user, category=category).annotate(
            likes_cnt=Count('likes_community', distinct=True)
        )
        return queryset

# 내가 작성한 common 게시물 목록 조회
class MyPostCommonViewSet(generics.ListAPIView):
    serializer_class = MyPostCommunityListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        category = 'common'

        queryset = Community.objects.filter(writer=user, category=category).annotate(
            likes_cnt=Count('likes_community', distinct=True)
        )
        return queryset

# 내가 작성한 qna 게시물 목록 조회
class MyPostQnaViewSet(generics.ListAPIView):
    serializer_class = MyPostCommunityListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        category = 'qna'

        queryset = Community.objects.filter(writer=user, category=category).annotate(
            likes_cnt=Count('likes_community', distinct=True)
        )
        return queryset
    
# 내가 작성한 건의사항 목록 조회
class MySuggestionViewSet(generics.ListAPIView):
    serializer_class = MySuggestionListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return Suggestion.objects.filter(writer=user)

# 내가 단 댓글   
# 내가 단 전체 댓글 목록 조회(커뮤+ai서비스 후기)
class MyAllCommentViewSet(generics.ListAPIView):
    serializer_class = CommunityCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return CommunityComment.objects.filter(writer=user) 
    
# 내가 단 tip 댓글 목록 조회
class MyTipCommentViewSet(generics.ListAPIView):
    serializer_class = MyCommunityCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return CommunityComment.objects.filter(writer=user, community__category='tip')
    
# 내가 단 common 댓글 목록 조회
class MyCommonCommentViewSet(generics.ListAPIView):
    serializer_class = MyCommunityCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return CommunityComment.objects.filter(writer=user, community__category='common')
    
# 내가 단 qna 댓글 목록 조회
class MyQnaCommentViewSet(generics.ListAPIView):
    serializer_class = MyCommunityCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return CommunityComment.objects.filter(writer=user, community__category='qna')
    
# 내가 단 ai 서비스 후기 목록 조회
class MyAiCommentViewSet(generics.ListAPIView):
    serializer_class = MyAiCommentListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return AiComment.objects.filter(writer=user)