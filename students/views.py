from django.core.mail import send_mail

from rest_framework import generics
from drf_spectacular.utils import extend_schema

from core.models import User, OTP
from .serializers import CreateStudentSerializer

from futaverse.views import PublicGenericAPIView

@extend_schema(tags=['Auth'])
class CreateStudentView(generics.CreateAPIView, PublicGenericAPIView):
    serializer_class = CreateStudentSerializer
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        existing_inactive_user = User.objects.filter(email=email, is_active=False).first()
        if existing_inactive_user:
            existing_inactive_user.delete()  

        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        user = serializer.save()
        otp = OTP.generate_otp(user)
        
        send_mail(
            subject="Verify your email",
            message=(
                f"Enter the OTP below into the required field \n"
                f"The OTP will expire in 10 mins\n\n"
                f"OTP: {otp}\n\n"
                f"If you did not initiate this request, please contact .................com\n\n"
                f"From the FutaVerse Team"
            ),
            recipient_list=[user.email],
            from_email=None,
        )