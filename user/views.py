from rest_framework import viewsets, status, mixins
from django.shortcuts import render
from .serializers import UserSerializer
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

class SignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        # JWT 토큰 생성
        user_data = response.data  # 새로 생성된 사용자 정보가 담겨 있는 response.data를 가져옴
        user = self.serializer_class.Meta.model(**user_data)  # 새로운 사용자 객체를 생성

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        # 토큰을 응답에 포함시켜 반환
        response.data['access'] = access
        response.data['refresh'] = str(refresh)

        return response


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
                'email': user.email,
                'access': access,
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)