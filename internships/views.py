from rest_framework import viewsets, permissions, filters, generics, status
from drf_spectacular.utils import extend_schema

from .models import Internship, InternshipApplication
from .serializers import InternshipSerializer, UpdateInternshipSerializer, InternshipStatusSerializer, CreateInternshipOfferSerializer, InternshipApplicationSerializer

@extend_schema(tags=['Internships'])
class ListCreateInternshipView(generics.ListCreateAPIView):
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer

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
    serializer_class = InternshipApplicationSerializer
    
    def perform_create(self, serializer):
        student = self.request.user.student_profile
        serializer.save(student=student)
        
    # TODO: Send notification to alumni when an application is submitted 