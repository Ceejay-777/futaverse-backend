from django.urls import path

from .views import ListCreateInternshipView, UpdateInternshipView, ToggleInternshipActiveView, CreateInternshipOfferView, ListInternshipOfferView, CreateInternshipApplication, CreateInternshipApplication, UploadApplicationResumeView

urlpatterns = [
    path('', ListCreateInternshipView.as_view(), name='list-create-internships'),
    path('/<int:pk>', UpdateInternshipView.as_view(), name='update-internship'),
    path('/<int:pk>/toggle-active', ToggleInternshipActiveView.as_view(), name='toggle-internship-active'),
    path('/offer', CreateInternshipOfferView.as_view(), name='create-internship-offers'),
    path('/offers', ListInternshipOfferView.as_view(), name='list-internship-offers'),
    path('/apply', CreateInternshipApplication.as_view(), name='create-internship-application'),
    path('/applications', CreateInternshipApplication.as_view(), name='list-create-internship-applications'),
    path('/upload-resume', UploadApplicationResumeView.as_view(), name='upload-application-resume'),
]
    