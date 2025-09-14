from django.contrib import admin
from django.urls import path, include
from core.views import UploadUserProfileImageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/profile-img', UploadUserProfileImageView.as_view(), name='upload-profile-image'),
    # path('alumni', include('alumnus.urls'))
]
