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
        serializer.save()
        
        print(serializer.data)
        # image_id = serializer.data.get('id')
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    