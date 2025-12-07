from django.urls import path
from .views import CreateEventView

urlpatterns = [
    path('', CreateEventView.as_view(), name='create-event'),
]