from rest_framework import serializers
from .models import UserProfileImage

class UserProfileImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfileImage
        fields = ['id']