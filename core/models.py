from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from datetime import timedelta
from cloudinary.models import CloudinaryField

from futaverse.utils.generate import generate_otp

def default_expiry():
    return timezone.now() + timedelta(minutes=10)

class User(AbstractBaseUser):
    class Role(models.TextChoices):
        MENTOR = 'Mentor', 'mentor'
        MENTEE = 'Mentee', 'mentee'
        STAFF = 'Staff', 'staff'
        ADMIN = 'admin', 'Admin'
        
    class Gender(models.TextChoices):
        MALE = 'Male', 'male'
        FEMALE = 'Female', 'female'
        OTHER = 'Other', 'other'
        UNKNOWN = 'Unknown', 'unknown'
        
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_num = models.CharField()
    role = models.CharField(max_length=20, choices=Role.choices)
    gender = models.CharField(choices=Gender.choices)
        
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, blank=True)
    
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    
    def get_profile(self, type_):
        if type_ == 'mentor':
            return getattr(self, 'mentor_profile', None)
        elif type_ == 'mentee':
            return getattr(self, 'mentee_profile', None)
        return None
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="otp")
    otp = models.CharField(max_length=6)  
    expiry = models.DateTimeField(default=default_expiry)
    verified = models.BooleanField(default=False)
    
    @classmethod
    def generate_otp(cls, user, expiry_minutes=10):
        """Create or replace OTP for a user"""
        otp = generate_otp()
        expiry_time = timezone.now() + timedelta(minutes=expiry_minutes)

        otp, _ = cls.objects.update_or_create(
            user=user,
            defaults={
                "otp": otp,
                "expiry": expiry_time,
                "verified": False
            }
        )
        return otp

    def is_expired(self):
        return timezone.now() > self.expiry

    def verify(self, otp):
        if self.verified:
            return False, "OTP already used"

        if self.is_expired():
            return False, "This OTP has expired"

        if self.otp != otp:
            return False, "Invalid OTP"

        self.verified = True
        self.save(update_fields=["verified"])
        return True, "OTP verified successfully"
    
    def __str__(self):
        return self.otp
    
class UserProfileImage(models.Model):
    user = models.ForeignKey(User, related_name="profile_img", on_delete=models.CASCADE, null=True, blank=True)
    file = CloudinaryField("profile_images/") 
    uploaded_at = models.DateTimeField(auto_now_add=True)