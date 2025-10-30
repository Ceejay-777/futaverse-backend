from rest_framework import serializers

from .models import Internship, InternshipApplication, InternshipOffer, InternshipEngagement, ApplicationResume
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
        exclude = ['deleted_at', 'is_deleted', 'alumnus', 'created_at', 'updated_at', 'is_active']
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
        validated_intenrnship = super().validate_internship(internship)
        if not validated_intenrnship.is_active:
            raise serializers.ValidationError("This internship is inactive. You cannot send new offers.")
        
        return  validated_intenrnship
    
class CreateInternshipApplicationSerializer(serializers.ModelSerializer):
    internship = serializers.PrimaryKeyRelatedField(queryset=Internship.objects.all())
    resume = serializers.PrimaryKeyRelatedField(queryset=ApplicationResume.objects.all(), required=False, write_only=True)
    
    class Meta:
        model = InternshipApplication
        fields = ['internship', 'id', 'cover_letter', 'resume']
        read_only_fields = ['id', 'created_at', 'updated_at', 'student', 'status', 'created_at', 'updated_at', 'deleted_at', 'is_deleted']
        
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        
        internship = validated_data['internship']
        resume = validated_data.get('resume')
        
        student = self.context['request'].user.student_profile
        require_resume = internship.require_resume
        
        if InternshipApplication.objects.filter(internship=internship, student=student).exists():
            raise serializers.ValidationError({"detail": "You have already applied for this internship."})
        
        if internship.is_active is False:
            raise serializers.ValidationError({"detail": "This internship is no longer active."})
        
        if require_resume and not resume:
            raise serializers.ValidationError({"detail": "You must upload a resume before applying for this internship."})
        
        return validated_data
        
class ApplicationResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationResume
        fields = ['resume', 'id']
        read_only_fields = ['id', 'uploaded_at', 'application', 'student']
        
        
   


        