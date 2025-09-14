from django.db import models
from core.models import User

class AlumniProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alumni_profile")
    
    description = models.TextField(blank=True, null=True)
    
    matric_no = models.CharField(max_length=10)
    department = models.CharField(max_length=30)
    faculty = models.CharField(max_length=20)
    grad_year = models.CharField(max_length=5)
    
    current_job_title = models.CharField()
    current_company = models.CharField()
    industry = models.CharField()
    years_of_exp = models.IntegerField()
    previous_comps = models.JSONField(default=list, blank=True, null=True)
    
    linkedin_url = models.URLField(blank=True, null=True, max_length=200)
    github_url = models.URLField(blank=True, null=True, max_length=200)
    website_url = models.URLField(blank=True, null=True, max_length=200)
    x_url = models.URLField(blank=True, null=True, max_length=200)
    instagram_url = models.URLField(blank=True, null=True, max_length=200)
    facebook_url = models.URLField(blank=True, null=True, max_length=200)
    