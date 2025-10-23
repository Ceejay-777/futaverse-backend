from rest_framework import serializers

from .models import Internship, InternshipApplication, InternshipOffer, InternshipEngagement
from students.models import StudentProfile, StudentResume
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
        if not internship.is_active:
            raise serializers.ValidationError("This internship is inactive. You cannot send new offers.")
        
        return  internship
    
class CreateInternshipApplicationSerializer(serializers.ModelSerializer):
    internship = serializers.PrimaryKeyRelatedField(queryset=Internship.objects.all())
    
    class Meta:
        model = InternshipApplication
        fields = ['internship', 'id', 'cover_letter']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        internship = validated_data['internship']
        student = validated_data['student']
        
        if InternshipApplication.objects.filter(internship=internship, student=student).exists():
            raise serializers.ValidationError({"detail": "You have already applied for this internship."})

        if internship.require_resume:
            resume = getattr(student, 'resume', None)
            if not resume:
                raise serializers.ValidationError({
                    "resume": "This internship requires a resume, but none was found. Please upload one first."
                })
            validated_data['resume'] = resume

        return super().create(validated_data)
    
class InternshipApplicationSerializer(serializers.ModelSerializer):
    # internship = serializers.PrimaryKeyRelatedField(queryset=Internship.objects.all())
    # student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    
    class Meta:
        model = InternshipApplication
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at', 'is_deleted']
        
   


        