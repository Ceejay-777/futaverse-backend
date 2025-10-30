from django.urls import path

from .views import ListCreateInternshipView, UpdateInternshipView, ToggleInternshipActiveView, CreateInternshipOfferView, ListInternshipOfferView, ListInternshipApplicationsView, CreateInternshipApplication, UploadApplicationResumeView, AcceptApplicationView, RejectApplicationView

urlpatterns = [
    path('', ListCreateInternshipView.as_view(), name='list-create-internships'),
    path('/<int:pk>', UpdateInternshipView.as_view(), name='update-internship'),
    path('/<int:pk>/toggle-active', ToggleInternshipActiveView.as_view(), name='toggle-internship-active'),
    path('/offer', CreateInternshipOfferView.as_view(), name='create-internship-offers'),
    path('/offers', ListInternshipOfferView.as_view(), name='list-internship-offers'),
    path('/apply', CreateInternshipApplication.as_view(), name='create-internship-application'),
    path('/applications', ListInternshipApplicationsView.as_view(), name='list-create-internship-applications'),
    path('/upload-resume', UploadApplicationResumeView.as_view(), name='upload-application-resume'),
    path('/applications/<int:application_id>/accept', AcceptApplicationView.as_view(), name='accept-internship-application'),
    path('/applications/<int:application_id>/reject', RejectApplicationView.as_view(), name='reject-internship-application'),
]
    