from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView, DashboardSummaryView
   
  


from .views import *

# Creamos el router y registramos todos los ViewSets
router = DefaultRouter()

# Módulo de Autenticación (image_6caa5a.png)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)
router.register(r'recursos', RecursoViewSet)
router.register(r'usuario-roles', UsuarioHasRolViewSet)
router.register(r'recurso-roles', RecursoHasRolViewSet)

# Módulo IoT (jeiner_playa_2.png)
router.register(r'zonas', ZonaMonitoreoViewSet)
router.register(r'dispositivos', DispositivoIotViewSet)
router.register(r'tipos-variables', TipoVariableViewSet)
router.register(r'sensores', SensorViewSet)
router.register(r'lecturas', LecturaSensorViewSet)
router.register(r'estados-ambientales', EstadoAmbientalViewSet)
router.register(r'umbrales', UmbralAlertaViewSet)
router.register(r'alertas', AlertaViewSet)
router.register(r'buzzers', BuzzerViewSet)
router.register(r'estados-buzzer', EstadoBuzzerViewSet)
router.register(r'comandos', ComandoRemotoViewSet)
router.register(r'respuestas-comandos', RespuestaComandoViewSet)
router.register(r'auditoria', AuditoriaSistemaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard-summary/', DashboardSummaryView.as_view(), name='dashboard_summary'),
    path('esp32/upload/', ESP32UploadView.as_view(), name='esp32_upload'),
]