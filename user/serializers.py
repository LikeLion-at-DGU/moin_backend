from .models import User, Job
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
            description=validated_data['description'],
        )

        
        user = User.objects.create_user(**validated_data)

        return user

    class Meta:
        model = User
        fields = ['nickname', 'email', 'job', 'description', 'password']