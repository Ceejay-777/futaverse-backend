from django.db import transaction

from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from drf_spectacular.utils import extend_schema

from .models import Internship, InternshipApplication, InternshipOffer, ApplicationResume
from .serializers import InternshipSerializer, UpdateInternshipSerializer, InternshipStatusSerializer, CreateInternshipOfferSerializer, CreateInternshipApplicationSerializer, ApplicationResumeSerializer

from core.models import User

from futaverse.permissions import IsAuthenticatedAlumnus, IsAuthenticatedStudent
from futaverse.utils.supabase import upload_file_to_supabase

from students.models import StudentResume

@extend_schema(tags=['Internships'])
class ListCreateInternshipView(generics.ListCreateAPIView):
    serializer_class = InternshipSerializer
    permission_classes = [IsAuthenticatedAlumnus]
    
    def get_queryset(self):
        user = self.request.user
        return Internship.objects.filter(alumnus=user.alumni_profile).select_related('alumnus')

@extend_schema(tags=['Internships']) 
class UpdateInternshipView(generics.UpdateAPIView):
    queryset = Internship.objects.all()
    serializer_class = UpdateInternshipSerializer
    http_method_names = ['patch']
    permission_classes = [IsAuthenticatedAlumnus]
    
@extend_schema(tags=['Internships'])
class ToggleInternshipActiveView(generics.UpdateAPIView):
    queryset = Internship.objects.all()
    serializer_class = InternshipStatusSerializer
    http_method_names = ['patch']
    permission_classes = [IsAuthenticatedAlumnus]
    
    def perform_update(self, serializer):
        internship = self.get_object()
        internship.toggle_active()
        
@extend_schema(tags=['Internships'])
class CreateInternshipOfferView(generics.CreateAPIView):
    serializer_class = CreateInternshipOfferSerializer
    permission_classes = [IsAuthenticatedAlumnus]
    
    # TODO: Send notification to student when an offer is created 
    
@extend_schema(tags=['Internships'])
class ListInternshipOfferView(generics.ListAPIView):
    serializer_class = CreateInternshipOfferSerializer
    permission_classes = [IsAuthenticatedAlumnus, IsAuthenticatedStudent]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return InternshipOffer.objects.filter(internship__alumnus=user.alumni_profile).select_related('internship', 'student', 'resume')
        
        elif user.role == User.Role.STUDENT:
            return InternshipOffer.objects.filter(student=user.student_profile).select_related('internship', 'resume', 'student')
    
@extend_schema(tags=['Internships'])
class CreateInternshipApplication(generics.CreateAPIView):
    serializer_class = CreateInternshipApplicationSerializer
    permission_classes = [IsAuthenticatedStudent]
    
    @transaction.atomic
    def perform_create(self, serializer):
        resume = serializer.validated_data.pop('resume', None)
        student = self.request.user.student_profile
        
        application = serializer.save(student=student)
        if resume:
            resume.application = application
            resume.save(update_fields=['application'])
        
    # TODO: Send notification to alumni when an application is submitted 
    
@extend_schema(tags=['Internships'])
class ListInternshipApplicationsView(generics.ListAPIView):
    serializer_class = CreateInternshipApplicationSerializer
    permission_classes = [IsAuthenticatedAlumnus, IsAuthenticatedStudent]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return InternshipApplication.objects.filter(internship__alumnus=user.alumni_profile).select_related('internship', 'student', 'resume')
        
        elif user.role == User.Role.STUDENT:
            return InternshipApplication.objects.filter(student=user.student_profile).select_related('internship', 'resume', 'student')
        
@extend_schema(tags=['Internships'])
class UploadApplicationResumeView(generics.CreateAPIView):
    queryset = ApplicationResume.objects.all()
    serializer_class = ApplicationResumeSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticatedStudent]
    
    def create(self, request, *args, **kwargs):
        resume = request.FILES.get('resume')
        student = request.user.student_profile
        
        if not resume:
            return Response({"detail": "Resume not provided", "status": "error"}, status=status.HTTP_400_BAD_REQUEST)
        
        resume_url = upload_file_to_supabase(resume, 'application_resumes/')
        
        serializer = self.get_serializer(data={'resume': resume_url})
        serializer.is_valid(raise_exception=True)
        serializer.save(student=student)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        