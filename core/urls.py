from django.urls import path
from .views import CreateAlumnusView, UploadUserProfileImageView

urlpatterns = [
    path('/profile-img', UploadUserProfileImageView.as_view(), name='upload-profile-image'),
    path('/signup/alumnus', CreateAlumnusView.as_view(), name='create-alumnus')
]