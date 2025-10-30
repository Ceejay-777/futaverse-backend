from rest_framework import serializers

from .models import StudentProfile
from core.models import User, UserProfileImage

from .models import StudentResume

class StudentProfileSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    profile_img = serializers.PrimaryKeyRelatedField(queryset=UserProfileImage.objects.all(), required=False)
    
    class Meta:
        model = StudentProfile
        exclude = ['user']

class CreateStudentSerializer(serializers.ModelSerializer):
    profile = StudentProfileSerializer(required=True, source='student_profile')
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    
    class Meta:
        model = User
        exclude = ['is_active', 'is_staff', 'role', 'last_login']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        profile_data = validated_data.pop('student_profile')
        profile_img = profile_data.pop('profile_img', None)
        
        validated_data['role'] = User.Role.STUDENT
        user = super().create(validated_data)
        StudentProfile.objects.create(user=user, **profile_data)
        
        if profile_img:
            profile_img.user = user
            profile_img.save()
        
        return user
    
class StudentResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentResume
        fields = ['resume']
        read_only_fields = ['id', 'student', 'uploaded_at']

    
