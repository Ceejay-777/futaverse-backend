from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

import uuid

from core.models import User

from futaverse.models import BaseModel
from decimal import Decimal

class Event(BaseModel):
    class Mode(models.TextChoices):
        VIRTUAL = "virtual", "Virtual"
        PHYSICAL = "physical", "Physical"
        HYBRID = "hybrid", "Hybrid"
        
    class Category(models.TextChoices):
        WORKSHOP = "workshop", "Workshop"
        TALK = "talk", "Talk"
        CAREER = "career", "Career"
        DONATION = "donation", "Donation"
        NETWORKING = "networking", "Networking"
        SYMPOSIUM = "symposium", "Symposium"
        TRAINING = "training", "Training"
        OTHER = "other", "Other"

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")

    title = models.CharField(max_length=320)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=Category.choices)
    mode = models.CharField(max_length=20, choices=Mode.choices)
    
    venue = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField()
    duration_mins = models.IntegerField(default=60, validators=[
        MinValueValidator(0)
    ])

    max_capacity = models.IntegerField(blank=True, null=True, validators=[
        MinValueValidator(0)
    ])
    allow_sponsorship = models.BooleanField(default=False)
    allow_donations = models.BooleanField(default=False)

    # boost_type = models.CharField(
    #     max_length=20, choices=BOOST_CHOICES, default="none"
    # )

    google_event_id = models.CharField(max_length=255, blank=True, null=True)
    google_meet_link = models.URLField(blank=True, null=True)

    is_cancelled = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title
    
class Ticket(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")

    name = models.CharField(max_length=255) 
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[
        MinValueValidator(0)
    ])
    discount_perc = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])
    quantity = models.IntegerField(validators=[
        MinValueValidator(0)
    ])  
    quantity_sold = models.IntegerField(default=0)

    sales_start = models.DateTimeField(default=timezone.now)
    sales_end = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"
    
    @property
    def sales_price(self):
        price = self.price
        discount = self.discount_perc

        if discount > 0:
            discount_amount = (discount / Decimal("100")) * price
            return price - discount_amount

        return price

class TicketPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchased_tickets")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="purchases")

    ticket_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    payment_reference = models.CharField(max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.ticket_uid} - {self.ticket.name}"