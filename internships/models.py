from django.db import models
from alumnus.models import AlumniProfile
from students.models import StudentProfile
from cloudinary.models import CloudinaryField
from futaverse.models import BaseModel
import cloudinary.utils

from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django_storage_supabase.supabase import SupabaseStorage
from futaverse.storage import SupabaseStorage as CustomSupabaseStorage

class CustomPublicStorage(RawMediaCloudinaryStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure files are uploaded as public
        self.options = {
            'resource_type': 'raw',
            'type': 'upload',  # This makes it public by default
        }

class InternshipStatus(models.TextChoices):
        PENDING = 'Pending', 'pending'
        ACCEPTED = 'Accepted', 'accepted'
        REJECTED = 'Rejected', 'rejected'
        WITHDRAWN = 'Withdrawn', 'withdrawn'

class Internship(BaseModel, models.Model):
    class WorkMode(models.TextChoices):
        REMOTE = 'Remote', 'Remote'
        HYBRID = 'Hybrid', 'Hybrid'
        ONSITE = 'Onsite', 'Onsite'
        
    class EngagementType(models.TextChoices):
        FULL_TIME = 'Full-time', 'Full-time'
        PART_TIME = 'Part-time', 'Part-time'
        CONTRACT = 'Contract', 'Contract'
        
    alumnus = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='internships')
        
    title = models.CharField(max_length=255)
    description = models.TextField()
    work_mode = models.CharField(choices=WorkMode.choices, max_length=20) 
    engagement_type = models.CharField(choices=EngagementType.choices, max_length=20)
    location = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    skills_required = models.JSONField(default=list, blank=True)
    duration_weeks = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    stipend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_slots = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    require_resume = models.BooleanField(default=True)
    require_cover_letter = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def toggle_active(self):
        self.is_active = not self.is_active
        self.save(update_fields=['is_active'])

    def __str__(self):
        return f"{self.title} (internship)"
    
class InternshipApplication(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='internship_applications')
    
    # resume = CloudinaryField('resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(choices=InternshipStatus.choices, max_length=20, default=InternshipStatus.PENDING)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        unique_together = ('internship', 'student')

    def __str__(self):
        return f"Application of {self.student.full_name} for {self.internship.title}"
    
class InternshipOffer(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='offers')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='internship_offers')
    
    status = models.CharField(choices=InternshipStatus.choices, max_length=20, default=InternshipStatus.PENDING)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("internship", "student")
        
    def withdraw(self):
        self.status = InternshipStatus.WITHDRAWN
        self.save(update_fields=['status'])
        
    def accept(self):
        self.status = InternshipStatus.ACCEPTED
        self.save(update_fields=['status'])
        
    def reject(self):
        self.status = InternshipStatus.REJECTED
        self.save(update_fields=['status'])

    def __str__(self):
        return f"Offer to {self.student.full_name} for {self.internship.title}"
    
class InternshipEngagement(models.Model):
    class Source(models.TextChoices):
        APPLICATION = "application", "Application"
        OFFER = "offer", "Offer"
        
    class EngagementStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        TERMINATED = "terminated", "Terminated"
        
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='engagements')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='internship_engagements')
    alumnus = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='internship_engagements')    
    
    source = models.CharField(choices=Source.choices, max_length=20)
    source_id = models.PositiveIntegerField()
    status = models.CharField(choices=EngagementStatus.choices, max_length=20, default=EngagementStatus.ACTIVE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("internship", "student")
    
    @property
    def engagement(self):
        source = self.source
        if source == self.Source.APPLICATION:
            return InternshipApplication.objects.filter(pk=self.source_id).first()
        elif source == self.Source.OFFER:
            return InternshipOffer.objects.filter(pk=self.source_id).first()
        
    @property
    def is_active(self):
        
        return self.status == self.EngagementStatus.ACTIVE

    def __str__(self):
        return f"Engagement of {self.student.full_name} in {self.internship.title}"
    
    
class InternResume(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='resume', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', storage=CustomSupabaseStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resume of {self.student.full_name} uploaded at {self.uploaded_at}"