from django.urls import path
from .views import UploadUserProfileImageView, VerifySignupOTPView, LoginView, TokenRefreshView, ForgotPasswordView
from alumnus.views import CreateAlumnusView

urlpatterns = [
    path('/profile-img', UploadUserProfileImageView.as_view(), name='upload-profile-image'),
    path('/signup/alumnus', CreateAlumnusView.as_view(), name='create-alumnus'),
    path('/signup/verify-otp', VerifySignupOTPView.as_view(), name='verify-signup-otp'),
    path('/login', LoginView.as_view(), name='login'),
    path('/refresh', TokenRefreshView.as_view(), name='refresh'),
    path('/forgot-password', ForgotPasswordView.as_view(), name='forgot-password'),
]