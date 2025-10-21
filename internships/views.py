from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Internship, InternResume
from .serializers import InternshipSerializer, UpdateInternshipSerializer, InternshipStatusSerializer, CreateInternshipOfferSerializer, ResumeSerializer

from futaverse.extensions import upload_resume

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
    
    # Send notification to student when an offer is created 
    
@extend_schema(tags=['Internships'])
class UploadResumeView(generics.CreateAPIView):
    queryset = InternResume.objects.all()
    serializer_class = ResumeSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        user = request.user
        resume = request.FILES.get('resume')
        
        if not resume:
            return Response({"detail": "Resume not provided", "status": "error"}, status=status.HTTP_400_BAD_REQUEST)
        
        public_url = upload_resume(resume, user.student_profile.id)
        
        serializer = self.get_serializer(data={"resume": public_url, "student": user.student_profile.id, "filename": resume.name})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
