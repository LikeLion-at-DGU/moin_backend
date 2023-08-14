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
class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ['id', 'name']

class CustomJobField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        try:
            job = Job.objects.get(name=data)
            return job
        except Job.DoesNotExist:
            raise serializers.ValidationError("Invalid job name")

class UserSerializer(serializers.ModelSerializer):
    job = CustomJobField(queryset=Job.objects.all())
    
    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'description', 'job']

class SocialUserSerializer(serializers.ModelSerializer):
    job = CustomJobField(queryset=Job.objects.all())

    class Meta:
        model = User
        fields = ['nickname', 'job', 'description']

# 작성자 본인 확인 api
class CheckWriterSerializer(serializers.ModelSerializer):
    is_writer = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['is_writer']