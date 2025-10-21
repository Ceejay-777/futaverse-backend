from rest_framework import serializers

from .models import Internship, InternshipApplication, InternshipOffer, InternshipEngagement, InternResume
from students.models import StudentProfile
from alumnus.models import AlumniProfile

from futaverse.serializers import StrictFieldsMixin

class InternshipSerializer(serializers.ModelSerializer):
    alumnus = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all())
    skills_required = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = Internship
        exclude = ['is_active', 'deleted_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
class UpdateInternshipSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    skills_required = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = Internship
        exclude = ['deleted_at', 'is_deleted', 'alumnus', 'created_at', 'updated_at', 'require_resume', 'require_cover_letter', 'is_active']
        read_only_fields = ['id']
        
class InternshipStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = ['id', 'is_active']
        read_only_fields = ['id']
        
class CreateInternshipOfferSerializer(serializers.ModelSerializer):
    internship = serializers.PrimaryKeyRelatedField(queryset=Internship.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    
    class Meta:
        model = InternshipOffer
        fields = ['internship', 'student', 'id']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate_internship(self, internship):
        if not internship.is_active:
            raise serializers.ValidationError("This internship is inactive. You cannot send new offers.")
        
        return  internship
    
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternResume
        fields = '__all__'
    
#     internship = serializers.PrimaryKeyRelatedField(queryset=Internship.objects.all())
#     student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    
#     class Meta:
#         model = InternshipApplication
#         fields = ['internship', 'student', 'id']
#         read_only_fields = ['id', 'created_at', 'updated_at']


        