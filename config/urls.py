from django.urls import path, include
from core.custom_admin import grouped_admin_site
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', grouped_admin_site.urls),
    
    # Agrupamos todo lo que pertenezca a la API dentro del prefijo api/
    path('api/', include([
        path('', include('core.urls')), # Las URLs de tus sensores/dispositivos (ej: api/sensores/)
        path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Ahora sí: api/login/
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Ahora sí: api/token/refresh/
    ])),
]
