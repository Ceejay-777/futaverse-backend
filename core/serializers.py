from rest_framework import serializers
from .models import UserProfileImage, User
from alumnus.serializers import AlumniProfileSerializer
from alumnus.models import AlumniProfile

class UserProfileImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfileImage
        fields = ['id']
        
class CreateAlumnusSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    house_no = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=10)
    profile = AlumniProfileSerializer(required=True)
    
    class Meta:
        model = User
        fiels = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        role = validated_data.get('role')
        
        house_no = validated_data.pop('house_no', None)
        if house_no:
            validated_data['street'] = f'{house_no}, {validated_data['street']}'

        user = super().create(validated_data) 

        if role == User.Role.ALUMNI:
            AlumniProfile.objects.create(user=user, **profile_data)
            
        return user