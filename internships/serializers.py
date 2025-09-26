from rest_framework import serializers

from .models import Internship, InternshipApplication, InternshipOffer, InternshipEngagement
from students.models import StudentProfile
from alumnus.models import AlumniProfile

class InternshipSerializer(serializers.ModelSerializer):
    alumnus = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all())
    skills_required = serializers.ListField(child=serializers.CharField(), required=False)
    class Meta:
        model = Internship
        fields =  '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']