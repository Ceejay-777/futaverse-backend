from rest_framework import viewsets, permissions, filters, generics

from drf_spectacular.utils import extend_schema

from .models import Internship
from .serializers import InternshipSerializer

@extend_schema(tags=['Internships'])
class ListCreateInternshipView(generics.ListCreateAPIView):
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer
    