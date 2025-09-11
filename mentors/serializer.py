from rest_framework import serializers

from .models import MentorProfile
from core.models import User, UserProfileImage

class MentorProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MentorProfile
        fields = '__all__'
        exclude = ['user']

class MentorSerializer(serializers.ModelSerializer):
    profile = MentorProfileSerializer(required=True)
    house_no = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=10)
    profile_img = serializers.PrimaryKeyRelatedField(queryset=UserProfileImage.objects.all(), required=False)
    previous_comps = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['is_active', 'is_staff', 'role']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        profile_img = validated_data.pop('profile_img')
        house_no = validated_data.pop('house_no', None)
        
        if house_no:
            validated_data['street'] = f'{house_no}, {validated_data['street']}'
            
        user = super().create(validated_data)
        MentorProfile.objects.create(user=user, **profile_data)
        if profile_img:
            profile_img.user = user
            profile_img.save()
        
        return user
    
