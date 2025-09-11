from rest_framework import serializers
from .models import UserProfileImage

class ProfileImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfileImage
        fields = ['id']
        read_only_fields = ('id', 'uploaded_at', 'user')