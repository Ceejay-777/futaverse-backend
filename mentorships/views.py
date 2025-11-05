from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Mentorship, MentorshipOffer, MentorshipStatus, MentorshipEngagement, MentorshipApplication
from .serializers import MentorshipSerializer, MentorshipOfferSerializer, MentorshipApplicationSerializer
from .mixins import OfferValidationMixin
from core.models import User

from futaverse.permissions import IsAuthenticatedAlumnus, IsAuthenticatedStudent
from futaverse.utils.supabase import upload_file_to_supabase

@extend_schema(tags=['Mentorships'], summary='List (GET) and create (POST) mentorships (alumnus)')
class ListCreateMentorshipView(generics.ListCreateAPIView):
    serializer_class = MentorshipSerializer
    permission_classes = [IsAuthenticatedAlumnus]
    
    def get_queryset(self):
        user = self.request.user
        return Mentorship.objects.filter(alumnus=user.alumni_profile).select_related('alumnus')
    
    def perform_create(self, serializer):
        alumnus = self.request.user.alumni_profile
        serializer.save(alumnus=alumnus)

@extend_schema(tags=['Mentorships'], summary='Retrieve (GET), update (PATCH) and delete (DELETE) a mentorship by id (alumnus)')
class RetrieveUpdateDestroyMentorshipView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MentorshipSerializer
    permission_classes = [IsAuthenticatedAlumnus]
    http_method_names = ['get', 'patch', 'delete']
    
    def get_queryset(self):
        user = self.request.user
        return Mentorship.objects.filter(alumnus=user.alumni_profile).select_related('alumnus')
    
    def perform_destroy(self, instance):
        instance.soft_delete()
        
@extend_schema(tags=['Mentorships'], summary='Create a mentorship offer (alumnus)')
class CreateMentorshipOfferView(generics.CreateAPIView):
    serializer_class = MentorshipOfferSerializer
    permission_classes = [IsAuthenticatedAlumnus]
    
@extend_schema(tags=['Mentorships'], summary='List mentorship offers (alumnus and student)')
class ListMentorshipOfferView(generics.ListAPIView):
    serializer_class = MentorshipOfferSerializer
    permission_classes = [IsAuthenticatedAlumnus | IsAuthenticatedStudent]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return MentorshipOffer.objects.filter(mentorship__alumnus=user.alumni_profile).select_related('mentorship', 'student')
        
        elif user.role == User.Role.STUDENT:
            return MentorshipOffer.objects.filter(student=user.student_profile).select_related('mentorship', 'student')
        
        return MentorshipApplication.objects.none()
        
@extend_schema(tags=['Mentorships'], summary='Retrieve a mentorship offer by id (alumnus and student)')
class RetrieveMentorshipOfferView(generics.RetrieveAPIView):
    serializer_class = MentorshipOfferSerializer
    permission_classes = [IsAuthenticatedAlumnus | IsAuthenticatedStudent]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return MentorshipOffer.objects.filter(mentorship__alumnus=user.alumni_profile).select_related('mentorship', 'student', 'mentorship__alumnus')
        
        elif user.role == User.Role.STUDENT:
            return MentorshipOffer.objects.filter(student=user.student_profile).select_related('mentorship', 'student')
        
@extend_schema(tags=['Mentorships'], summary='Accept a mentorship offer (student)')
class AcceptOfferView(OfferValidationMixin, APIView):
    permission_classes = [IsAuthenticatedStudent]
    serializer_class = None
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        offer = self.get_offer()
        
        mentorship = offer.mentorship
        student = offer.student
        alumnus = mentorship.alumnus
        
        if student != request.user.student_profile:
            return Response({"detail": "You are not authorized to accept this mentorship offer."}, status=status.HTTP_403_FORBIDDEN)
        
        if MentorshipEngagement.objects.filter(mentorship=mentorship, student=student).exists():
            return Response({"detail": "You are already engaged in this mentorship."}, status=status.HTTP_400_BAD_REQUEST)
        
        engagement = MentorshipEngagement.objects.create(
            mentorship=mentorship,
            student=student,
            alumnus= alumnus,
            source= MentorshipEngagement.Source.OFFER,
            source_id= offer.id,
        )
        
        offer.accept()
        mentorship.decrement_remaining_slots()
        return Response({"detail": "Offer accepted successfully.", "engagement_id": engagement.id},status=status.HTTP_201_CREATED)
    
@extend_schema(tags=['Mentorships'], summary='Reject a mentorship offer (student)')
class RejectOfferView(OfferValidationMixin, APIView):
    permission_classes = [IsAuthenticatedStudent]
    serializer_class = None
    
    def post(self, request, *args, **kwargs):
        offer = self.get_offer()
        
        if offer.student != request.user.student_profile:
            return Response({"detail": "You are not authorized to reject this mentorship."}, status=status.HTTP_403_FORBIDDEN)
        
        offer.reject()
        
        return Response({"detail": "Offer rejected successfully."},status=status.HTTP_200_OK)
    
@extend_schema(tags=['Mentorships'], summary='Withdraw a mentorship offer (alumnus)')
class WithdrawOfferView(OfferValidationMixin,APIView):
    permission_classes = [IsAuthenticatedAlumnus]
    serializer_class = None
    
    def post(self, request, *args, **kwargs):
        offer = self.get_offer(withdraw=True)
        
        if offer.mentorship.alumnus != request.user.alumni_profile:
            return Response({"detail": "You are not authorized to withdraw this application."}, status=status.HTTP_403_FORBIDDEN)
        
        if offer.status != MentorshipStatus.PENDING:
            raise ValidationError({"detail": "Only pending offers can be withdrawn."}, status=status.HTTP_400_BAD_REQUEST)
        
        offer.withdraw()
        
        return Response({"detail": "Offer withdrawn successfully."},status=status.HTTP_200_OK)
    
@extend_schema(tags=['Mentorships'], summary='Apply for a mentorship (student)')
class CreateMentorshipApplicationView(generics.CreateAPIView):
    permission_classes = [IsAuthenticatedStudent]
    serializer_class = MentorshipApplicationSerializer
    
@extend_schema(tags=['Mentorships'], summary='List mentorship applications (alumnus and student)')
class ListMentorshipApplicationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedAlumnus | IsAuthenticatedStudent]
    serializer_class = MentorshipApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return MentorshipApplication.objects.filter(mentorship__alumnus=user.alumni_profile).select_related('mentorship', 'student', 'mentorship__alumnus')
        
        elif user.role == User.Role.STUDENT:
            return MentorshipApplication.objects.filter(student=user.student_profile).select_related('mentorship', 'student')
        
        return MentorshipApplication.objects.none()
        
@extend_schema(tags=['Mentorships'], summary='Retrieve a mentorship application (alumnus and student)')
class RetrieveMentorshipApplicationView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticatedAlumnus | IsAuthenticatedStudent]
    serializer_class = MentorshipApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.ALUMNI:
            return MentorshipApplication.objects.filter(mentorship__alumnus=user.alumni_profile).select_related('mentorship', 'student', 'mentorship__alumnus')
        
        elif user.role == User.Role.STUDENT:
            return MentorshipApplication.objects.filter(student=user.student_profile).select_related('mentorship', 'student')
        
        return MentorshipApplication.objects.none()