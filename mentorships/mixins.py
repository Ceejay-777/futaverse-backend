from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ValidationError
from .models import MentorshipOffer, MentorshipStatus

class OfferValidationMixin:
    def get_offer(self, withdraw: bool = False) -> MentorshipOffer:
        offer_id = self.kwargs.get('offer_id')
        
        if not offer_id:
            raise ValidationError({"detail": "Offer ID is required."})
        
        offer = get_object_or_404(MentorshipOffer.objects.all().select_related("mentorship", "student", "mentorship__alumnus"), pk=offer_id)
        
        if offer.status == MentorshipStatus.WITHDRAWN:
            raise ValidationError({"detail": "Offer has already been withdrawn."})
        
        if not withdraw and offer.status != MentorshipStatus.PENDING:
            raise ValidationError({"detail": "Offer has already been responded to."})
    
        if not offer.mentorship.is_active:
                raise ValidationError({"detail": "Mentorship is not active."})
            
        return offer