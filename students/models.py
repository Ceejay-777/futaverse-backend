from django.db import models
from core.models import User

class LevelChoices(models.IntegerChoices):
    LEVEL_100 = 100, "100"
    LEVEL_200 = 200, "200"
    LEVEL_300 = 300, "300"
    LEVEL_400 = 400, "400"
    LEVEL_500 = 500, "500"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    
    description = models.TextField(blank=True, null=True)
    
    matric_no = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=30)
    faculty = models.CharField(max_length=20)
    level = models.IntegerField(choices=LevelChoices.choices)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2)
    skills = models.JSONField(default=list)
    expected_grad_year = models.CharField(max_length=4)
    
    preferred_industry = models.CharField()
    preferred_company_type = models.CharField()
    willingness_to_relocate = models.BooleanField()
    willingness_to_be_mentored = models.BooleanField(default=True)
    
    linkedin_url = models.URLField(blank=True, null=True, max_length=200)
    github_url = models.URLField(blank=True, null=True, max_length=200)
    website_url = models.URLField(blank=True, null=True, max_length=200)
    x_url = models.URLField(blank=True, null=True, max_length=200)
    instagram_url = models.URLField(blank=True, null=True, max_length=200)
    facebook_url = models.URLField(blank=True, null=True, max_length=200)
    
    @property
    def full_name(self):
        return f"{self.user.firstname} {self.user.lastname}"
    
    def __str__(self):
        return f"{self.full_name} (student)"
    
class StudentResume(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='resume', blank=True, null=True)
    resume = models.URLField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resume of {self.student.full_name} uploaded at {self.uploaded_at}"
    