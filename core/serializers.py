from rest_framework import serializers
from .models import UserProfileImage, User
from alumnus.serializers import AlumniProfileSerializer
from alumnus.models import AlumniProfile

class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileImage
        fields = ['id', 'image']
        
class CreateAlumnusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['last_login', 'is_staff', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    alumni_profile = AlumniProfileSerializer(required=True, source='alumni_profile')
        
    def create(self, validated_data):
        profile_data = validated_data.pop('alumni_profile')
        role = validated_data.get('role')
        
        house_no = profile_data.pop('house_no', None)
        if house_no:
            validated_data['street'] = f'{house_no}, {validated_data['street']}'

        user = super().create(validated_data) 

        if role == User.Role.ALUMNI:
            AlumniProfile.objects.create(user=user, **profile_data)
            
        return user