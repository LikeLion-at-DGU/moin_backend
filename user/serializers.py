from .models import User, Job
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        job_name = validated_data['job']
        
        try:
            job_instance = Job.objects.get(name=job_name)
        except Job.DoesNotExist:
            raise serializers.ValidationError(f"Job with name '{job_name}' does not exist.")
        
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
            description=validated_data['description'],
            job=job_instance,
        )        
        return user

    class Meta:
        model = User
        fields = ['nickname', 'email', 'job', 'description', 'password']