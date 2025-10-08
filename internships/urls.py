from django.urls import path

from .views import ListCreateInternshipView, UpdateInternshipView, ToggleInternshipActiveView, CreateInternshipOfferView, UploadResumeView

urlpatterns = [
    path('', ListCreateInternshipView.as_view(), name='list-create-internships'),
    path('/<int:pk>', UpdateInternshipView.as_view(), name='update-internship'),
    path('/<int:pk>/toggle-active', ToggleInternshipActiveView.as_view(), name='toggle-internship-active'),
    path('/offer', CreateInternshipOfferView.as_view(), name='offer-internship'),
    path('/resume', UploadResumeView.as_view(), name='upload-resume'),
]
    