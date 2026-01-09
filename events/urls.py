from django.urls import path
from .views import CreateEventView, CreateTicketView, CreateTicketPurchaseView

urlpatterns = [
    path('', CreateEventView.as_view(), name='create-event'),
    path('/ticket', CreateTicketView.as_view(), name='create-ticket'),
    path('/register', CreateTicketPurchaseView.as_view(), name='create-ticket-purchase'),
]