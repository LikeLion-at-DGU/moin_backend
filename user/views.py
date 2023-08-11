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

from .serializers import UserLoginSerializer, UserRegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .models import User, Job

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

        print(user)
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