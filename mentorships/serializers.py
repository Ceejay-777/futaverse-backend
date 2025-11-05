from rest_framework import serializers

from .models import Mentorship, MentorshipOffer, MentorshipApplication, MentorshipRequest
from students.models import StudentProfile
from alumnus.models import AlumniProfile

from futaverse.serializers import StrictFieldsMixin

class MentorshipSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Mentorship
        exclude = ['is_active', 'deleted_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'alumnus', 'remaining_slots']
        
class MentorshipOfferSerializer(serializers.ModelSerializer):
    mentorship = serializers.PrimaryKeyRelatedField(queryset=Mentorship.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    
    class Meta:
        model = MentorshipOffer
        exclude = ['deleted_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'responded_at']
        
class MentorshipApplicationSerializer(serializers.ModelSerializer):
    mentorship = serializers.PrimaryKeyRelatedField(queryset=Mentorship.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    
    class Meta:
        model = MentorshipApplication
        exclude = ['deleted_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'responded_at']