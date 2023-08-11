from .models import User, Job
from rest_framework import serializers

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