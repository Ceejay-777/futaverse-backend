# from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
     path('', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/raw', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger-ui', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('admin/', admin.site.urls),
    # path('alumni', include('alumnus.urls')),
    path('api/auth', include('core.urls'))
]
