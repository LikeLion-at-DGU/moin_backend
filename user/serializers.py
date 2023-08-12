from .models import User, Job
from rest_framework import serializers
from dj_rest_auth.serializers import PasswordChangeSerializer

class UserRegisterSerializer(serializers.ModelSerializer):
    job = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['nickname', 'email', 'job', 'description', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirm = serializers.CharField(write_only=True)

class CustomPasswordChangeSerializer(PasswordChangeSerializer):
    origin_password = serializers.CharField(required=True)

## Profile을 위한 시리얼라이저

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'description', 'job']