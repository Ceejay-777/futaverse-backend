# from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from core.views import UploadUserProfileImageView

urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/raw', SpectacularAPIView.as_view(), name='schema'),
    
    path('api/profile-img', UploadUserProfileImageView.as_view(), name='upload-profile-image'),
    path('api/auth', include('core.urls')),
    path('api/internships', include('internships.urls')),
    path('api/students', include('students.urls'))
]
