from django.urls import path

from .views import ListCreateInternshipView

urlpatterns = [
    path('', ListCreateInternshipView.as_view(), name='list-create-internships'),
]
    