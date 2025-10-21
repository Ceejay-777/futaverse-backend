from django.urls import path

from .views import ListCreateInternshipView, UpdateInternshipView, ToggleInternshipActiveView, CreateInternshipOfferView, ApplyForInternshipView

urlpatterns = [
    path('', ListCreateInternshipView.as_view(), name='list-create-internships'),
    path('/<int:pk>', UpdateInternshipView.as_view(), name='update-internship'),
    path('/<int:pk>/toggle-active', ToggleInternshipActiveView.as_view(), name='toggle-internship-active'),
    path('/offer', CreateInternshipOfferView.as_view(), name='offer-internship'),
    path('/apply', ApplyForInternshipView.as_view(), name='apply-to-internship'),
]
    