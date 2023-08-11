from rest_framework import viewsets, status, mixins
from django.shortcuts import render
from .serializers import UserSerializer, UserRegisterSerializer
from .models import User, Job
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class SignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def create(self, request):
        job_name = request.data.pop('job_name')  # job_name 가져오기
        job = Job.objects.get(name=job_name)  # 해당 이름의 Job 모델을 찾거나 생성
        user_data = request.data
        user_data['job'] = job
        user = User.objects.create(**user_data)

        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        res = Response(
            {
                "user": {
                    'nickname': user.nickname,
                    'email': user.email,
                    'description' : user.description,
                    'job': user.job.name,
                    'password' : user.password
                },
                "message": "register successs",
                "token": {
                    "access": access_token,
                    "refresh": refresh_token,
                },
            },
            status=status.HTTP_200_OK,
            )
        return res

class LoginViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            return Response({
                'nickname': user.nickname,
                'email': user.email,
                'description' : user.description,
                'job': user.job.name,
                'access': access,
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)