from django.urls import path

from .views import ListCreateInternshipView, ToggleInternshipActiveView, CreateInternshipOfferView, ListInternshipOfferView, ListInternshipApplicationsView, CreateInternshipApplication, UploadApplicationResumeView, AcceptApplicationView, RejectApplicationView, AcceptOfferView, RejectOfferView, RetrieveUpdateDestroyMentorshipView, RetrieveinternshipOfferView, RetrieveInternshipApplicationView, RetrieveInternshipEngagementView, WithdrawApplicationView, WithdrawOfferView, ListInternshipEngagementsView

urlpatterns = [
    path('', ListCreateInternshipView.as_view(), name='list-create-internships'),
    path('/<int:pk>', RetrieveUpdateDestroyMentorshipView.as_view(), name='retrieve-update-destroy-internships'),
    path('/<int:pk>/toggle-active', ToggleInternshipActiveView.as_view(), name='toggle-internship-active'),
    
    path('/offer', CreateInternshipOfferView.as_view(), name='create-internship-offers'),
    path('/offers', ListInternshipOfferView.as_view(), name='list-internship-offers'),
    path('/offers/<int:pk>', RetrieveinternshipOfferView.as_view(), name='retrieve-internship-offers'),
    path('/offers/<int:offer_id>/accept', AcceptOfferView.as_view(), name='accept-internship-offer'),
    path('/offers/<int:offer_id>/reject', RejectOfferView.as_view(), name='reject-internship-offer'),
    path('/offers/<int:offer_id>/withdraw', WithdrawOfferView.as_view(), name='withdraw-internship-offer'),
    
    path('/application', CreateInternshipApplication.as_view(), name='create-internship-application'),
    path('/applications', ListInternshipApplicationsView.as_view(), name='list-create-internship-applications'),
    path('/applications/<int:pk>', RetrieveInternshipApplicationView.as_view(), name='retrieve-internship-application'),
    path('/upload-resume', UploadApplicationResumeView.as_view(), name='upload-application-resume'),
    path('/applications/<int:application_id>/accept', AcceptApplicationView.as_view(), name='accept-internship-application'),
    path('/applications/<int:application_id>/reject', RejectApplicationView.as_view(), name='reject-internship-application'),
    path('/applications/<int:application_id>/withdraw', WithdrawApplicationView.as_view(), name='withdraw-internship-application'),
    
    path('/engagements', ListInternshipEngagementsView.as_view(), name='list-internship-engagements'),
    path('/engagements/<int:pk>', RetrieveInternshipEngagementView.as_view(), name='retrieve-internship-engagement'),
]
    