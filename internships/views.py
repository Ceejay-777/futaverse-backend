from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Internship, InternshipApplication, InternshipOffer, ApplicationResume, InternshipEngagement, InternshipStatus
from .serializers import InternshipSerializer, UpdateInternshipSerializer, InternshipStatusSerializer, CreateInternshipOfferSerializer, CreateInternshipApplicationSerializer, ApplicationResumeSerializer, InternshipEngagementSerializer

from core.models import User

from futaverse.permissions import IsAuthenticatedAlumnus, IsAuthenticatedStudent
from futaverse.utils.supabase import upload_file_to_supabase


@extend_schema(tags=['Internships'])
class ListCreateInternshipView(generics.ListCreateAPIView):
    serializer_class = InternshipSerializer
    permission_classes = [IsAuthenticatedAlumnus]
    
    def get_queryset(self):
        user = self.request.user
        return Internship.objects.filter(alumnus=user.alumni_profile).select_related('alumnus')
    
    def perform_create(self, serializer):
        alumnus = self.request.user.alumni_profile
        serializer.save(alumnus=alumnus)

@extend_schema(tags=['Internships']) 
class UpdateInternshipView(generics.UpdateAPIView):
    serializer_class = UpdateInternshipSerializer
    http_method_names = ['patch']
    permission_classes = [IsAuthenticatedAlumnus]
    
    def get_queryset(self):
        user = self.request.user
        return Internship.objects.filter(alumnus=user.alumni_profile).select_related('alumnus')
    
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
    permission_classes = [IsAuthenticatedAlumnus | IsAuthenticatedStudent]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return InternshipOffer.objects.filter(internship__alumnus=user.alumni_profile).select_related('internship', 'student')
        
        elif user.role == User.Role.STUDENT:
            return InternshipOffer.objects.filter(student=user.student_profile).select_related('internship', 'student')
    
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
    permission_classes = [IsAuthenticatedAlumnus | IsAuthenticatedStudent]
    
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
    
@extend_schema(tags=['Internships'])
class AcceptApplicationView(APIView):
    permission_classes = [IsAuthenticatedAlumnus]
    serializer_class = None
    
    def get_object(self):
        application_id = self.kwargs.get('application_id')
        if not application_id:
            raise ValidationError({"detail": "Application ID is required."})
        
        return get_object_or_404(InternshipApplication.objects.filter(status=InternshipStatus.PENDING), pk=application_id)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        application = self.get_object()
        
        internship = application.internship
        student = application.student
        alumnus = internship.alumnus
        
        if internship.alumnus != request.user.alumni_profile:
            return Response({"detail": "You are not authorized to manage this internship."}, status=status.HTTP_403_FORBIDDEN)
        
        if InternshipEngagement.objects.filter(internship=internship, student=student).exists():
            return Response({"detail": "This student is already engaged in this internship."}, status=status.HTTP_400_BAD_REQUEST)
        
        engagement = InternshipEngagement.objects.create(
            internship=internship,
            student=student,
            alumnus= alumnus,
            source=InternshipEngagement.Source.APPLICATION,
            source_id=application.id,
        )
        
        application.accept()
        return Response({"detail": "Application accepted successfully.", "engagement_id": engagement.id},status=status.HTTP_201_CREATED)
    
@extend_schema(tags=['Internships'])
class RejectApplicationView(APIView):
    permission_classes = [IsAuthenticatedAlumnus]
    serializer_class = None
    
    def get_object(self):
        application_id = self.kwargs.get('application_id')
        if not application_id:
            raise ValidationError({"detail": "Application ID is required."})
        
        return get_object_or_404(InternshipApplication.objects.filter(status=InternshipStatus.PENDING), pk=application_id)
    
    def post(self, request, *args, **kwargs):
        application = self.get_object()
        
        internship = application.internship
        
        if internship.alumnus != request.user.alumni_profile:
            return Response({"detail": "You are not authorized to manage this internship."}, status=status.HTTP_403_FORBIDDEN)
        
        application.reject()
        
        return Response({"detail": "Application rejected successfully."},status=status.HTTP_200_OK)
    
@extend_schema(tags=['Internships'])
class AcceptOfferView(APIView):
    permission_classes = [IsAuthenticatedStudent]
    serializer_class = None
    
    def get_object(self):
        offer_id = self.kwargs.get('offer_id')
        if not offer_id:
            raise ValidationError({"detail": "Offer ID is required."})
        
        offer = get_object_or_404(InternshipOffer.objects.filter(status=InternshipStatus.PENDING).select_related('internship'), pk=offer_id)
        
        if not offer.internship.is_active:
            raise ValidationError({"detail": "Internship is not active."})
        
        return offer
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        offer = self.get_object()
        
        internship = offer.internship
        student = offer.student
        alumnus = internship.alumnus
        
        if offer.student != request.user.student_profile:
            return Response({"detail": "You are not authorized to accept this internship offer."}, status=status.HTTP_403_FORBIDDEN)
        
        if InternshipEngagement.objects.filter(internship=internship, student=student).exists():
            return Response({"detail": "You are already engaged in this internship."}, status=status.HTTP_400_BAD_REQUEST)
        
        engagement = InternshipEngagement.objects.create(
            internship=internship,
            student=student,
            alumnus= alumnus,
            source= InternshipEngagement.Source.OFFER,
            source_id= offer.id,
        )
        
        offer.accept()
        return Response({"detail": "Application accepted successfully.", "engagement_id": engagement.id},status=status.HTTP_201_CREATED)
    
@extend_schema(tags=['Internships'])
class RejectOfferView(APIView):
    permission_classes = [IsAuthenticatedStudent]
    serializer_class = None
    
    def get_object(self):
        offer_id = self.kwargs.get('offer_id')
        if not offer_id:
            raise ValidationError({"detail": "Offer ID is required."})
        
        return get_object_or_404(InternshipOffer.objects.filter(status=InternshipStatus.PENDING), pk=offer_id)
    
    def post(self, request, *args, **kwargs):
        offer = self.get_object()
        
        if offer.student != request.user.student_profile:
            return Response({"detail": "You are not authorized to reject this internship."}, status=status.HTTP_403_FORBIDDEN)
        
        offer.reject()
        
        return Response({"detail": "Application rejected successfully."},status=status.HTTP_200_OK)

@extend_schema(tags=['Internships'])
class WithdrawApplicationView(APIView):
    permission_classes = [IsAuthenticatedStudent]
    serializer_class = None
    
    def get_object(self):
        application_id = self.kwargs.get('application_id')
        if not application_id:
            raise ValidationError({"detail": "Application ID is required."})
        
        return get_object_or_404(InternshipApplication.objects.filter(status=InternshipStatus.PENDING), pk=application_id)
    
    def post(self, request, *args, **kwargs):
        application = self.get_object()
        
        if application.student != request.user.student_profile:
            return Response({"detail": "You are not authorized to withdraw this application."}, status=status.HTTP_403_FORBIDDEN)
        
        application.withdraw()
        
        return Response({"detail": "Application withdrawn successfully."},status=status.HTTP_200_OK)
    
@extend_schema(tags=['Internships'])
class WithdrawOfferView(APIView):
    permission_classes = [IsAuthenticatedAlumnus]
    serializer_class = None
    
    def get_object(self):
        offer_id = self.kwargs.get('offer_id')
        if not offer_id:
            raise ValidationError({"detail": "Offer ID is required."})
        
        return get_object_or_404(InternshipOffer.objects.filter(status=InternshipStatus.PENDING), pk=offer_id)
    
    def post(self, request, *args, **kwargs):
        offer = self.get_object()
        
        if offer.internship.alumnus != request.user.alumni_profile:
            return Response({"detail": "You are not authorized to withdraw this application."}, status=status.HTTP_403_FORBIDDEN)
        
        offer.withdraw()
        
        return Response({"detail": "Offer withdrawn successfully."},status=status.HTTP_200_OK)
    
@extend_schema(tags=['Internships'])
class ListEngagementsView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedAlumnus | IsAuthenticatedStudent]
    serializer_class = InternshipEngagementSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return InternshipEngagement.objects.filter(alumnus=user.alumni_profile).select_related('internship', 'student')
        
        elif user.role == User.Role.STUDENT:
            return InternshipEngagement.objects.filter(student=user.student_profile).select_related('internship', 'alumnus')
        
        