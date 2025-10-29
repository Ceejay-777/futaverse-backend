from rest_framework import viewsets, permissions, filters, generics, status
from drf_spectacular.utils import extend_schema

from .models import Internship, InternshipApplication
from .serializers import InternshipSerializer, UpdateInternshipSerializer, InternshipStatusSerializer, CreateInternshipOfferSerializer, InternshipApplicationSerializer, CreateInternshipApplicationSerializer

from core.models import User

@extend_schema(tags=['Internships'])
class ListCreateInternshipView(generics.ListCreateAPIView):
    serializer_class = InternshipSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Internship.objects.filter(alumnus=user.alumni_profile).select_related('alumnus')

@extend_schema(tags=['Internships']) 
class UpdateInternshipView(generics.UpdateAPIView):
    queryset = Internship.objects.all()
    serializer_class = UpdateInternshipSerializer
    http_method_names = ['patch']
    # permission_classes = [permissions.IsAdminUser]
    
@extend_schema(tags=['Internships'])
class ToggleInternshipActiveView(generics.UpdateAPIView):
    queryset = Internship.objects.all()
    serializer_class = InternshipStatusSerializer
    http_method_names = ['patch']
    
    def perform_update(self, serializer):
        internship = self.get_object()
        internship.toggle_active()
        
@extend_schema(tags=['Internships'])
class CreateInternshipOfferView(generics.CreateAPIView):
    queryset = Internship.objects.all()
    serializer_class = CreateInternshipOfferSerializer
    
    # TODO: Send notification to student when an offer is created 
    
@extend_schema(tags=['Internships'])
class ApplyForInternshipView(generics.CreateAPIView):
    queryset = InternshipApplication.objects.all()
    serializer_class = CreateInternshipApplicationSerializer
    
    def perform_create(self, serializer):
        student = self.request.user.student_profile
        serializer.save(student=student)
        
    # TODO: Send notification to alumni when an application is submitted 
    
@extend_schema(tags=['Internships'])
class ListInternshipApplicationsView(generics.ListAPIView):
    serializer_class = InternshipApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return InternshipApplication.objects.filter(internship__alumnus=user.alumni_profile).select_related('internship', 'student', 'resume')
        
        elif user.role == User.Role.STUDENT:
            return InternshipApplication.objects.filter(student=user.student_profile).select_related('internship', 'resume')