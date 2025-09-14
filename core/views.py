from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import User, UserProfileImage
from .serializers import UserProfileImageSerializer

class UploadUserProfileImageView(generics.CreateAPIView):
    queryset = UserProfileImage.objects.all()
    serializer_class = UserProfileImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_image = serializer.save()
        
        print("Saved image:", saved_image.image)
        print("Image URL:", saved_image.image.url if saved_image.image else None)
        
        data = serializer.data
        
        return Response(data, status=status.HTTP_201_CREATED)
    