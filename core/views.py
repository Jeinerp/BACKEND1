from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication


class StandardPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class DashboardSummaryView(APIView):
    """Devuelve todos los datos del dashboard en una sola llamada."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        dispositivos = DispositivoIot.objects.all()
        sensores = Sensor.objects.all()
        alertas = Alerta.objects.all().order_by('-fecha_generacion')[:20]
        lecturas = LecturaSensor.objects.all().order_by('-fecha_hora')[:20]
        zonas = ZonaMonitoreo.objects.all()

        return Response({
            'dispositivos': DispositivoIotSerializer(dispositivos, many=True).data,
            'sensores': SensorSerializer(sensores, many=True).data,
            'alertas': AlertaSerializer(alertas, many=True).data,
            'lecturas': LecturaSensorSerializer(lecturas, many=True).data,
            'zonas': ZonaMonitoreoSerializer(zonas, many=True).data,
        })
# ==========================================
# 1. VISTAS DE AUTENTICACIÓN (image_6caa5a.png)
# ==========================================
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def perform_destroy(self, instance):
        from django.contrib.auth.models import User
        try:
            auth_user = User.objects.get(id=instance.idusuarios)
            auth_user.delete()
        except User.DoesNotExist:
            pass
        instance.delete()

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

class RecursoViewSet(viewsets.ModelViewSet):
    queryset = Recurso.objects.all()
    serializer_class = RecursoSerializer

class UsuarioHasRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioHasRol.objects.all()
    serializer_class = UsuarioHasRolSerializer

class RecursoHasRolViewSet(viewsets.ModelViewSet):
    queryset = RecursoHasRol.objects.all()
    serializer_class = RecursoHasRolSerializer

# ==========================================
# 2. VISTAS IOT (jeiner_playa_2.png)
# ==========================================

class ZonaMonitoreoViewSet(viewsets.ModelViewSet):
    queryset = ZonaMonitoreo.objects.all()
    serializer_class = ZonaMonitoreoSerializer

class DispositivoIotViewSet(viewsets.ModelViewSet):
    queryset = DispositivoIot.objects.all()
    serializer_class = DispositivoIotSerializer

class TipoVariableViewSet(viewsets.ModelViewSet):
    queryset = TipoVariable.objects.all()
    serializer_class = TipoVariableSerializer

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

class LecturaSensorViewSet(viewsets.ModelViewSet):
    queryset = LecturaSensor.objects.all().order_by('-fecha_hora')
    serializer_class = LecturaSensorSerializer
    pagination_class = StandardPagination

class EstadoAmbientalViewSet(viewsets.ModelViewSet):
    queryset = EstadoAmbiental.objects.all()
    serializer_class = EstadoAmbientalSerializer

class UmbralAlertaViewSet(viewsets.ModelViewSet):
    queryset = UmbralAlerta.objects.all()
    serializer_class = UmbralAlertaSerializer

class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all().order_by('-fecha_generacion')
    serializer_class = AlertaSerializer
    pagination_class = StandardPagination

class BuzzerViewSet(viewsets.ModelViewSet):
    queryset = Buzzer.objects.all()
    serializer_class = BuzzerSerializer

class EstadoBuzzerViewSet(viewsets.ModelViewSet):
    queryset = EstadoBuzzer.objects.all().order_by('-fecha_hora')
    serializer_class = EstadoBuzzerSerializer

class ComandoRemotoViewSet(viewsets.ModelViewSet):
    queryset = ComandoRemoto.objects.all()
    serializer_class = ComandoRemotoSerializer

class RespuestaComandoViewSet(viewsets.ModelViewSet):
    queryset = RespuestaComando.objects.all()
    serializer_class = RespuestaComandoSerializer

class AuditoriaSistemaViewSet(viewsets.ModelViewSet):
    queryset = AuditoriaSistema.objects.all().order_by('-fecha_hora')
    serializer_class = AuditoriaSistemaSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class ESP32UploadView(APIView):
    """
    Endpoint para recibir lecturas de sensores directamente de un dispositivo ESP32
    sin necesidad de autenticación por Token JWT.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from decimal import Decimal
        from django.utils import timezone
        
        print("ESP32 RECEIVED DATA:", request.data, flush=True)
        print("ESP32 CONTENT TYPE:", request.content_type, flush=True)
        mac = request.data.get('mac')
        if not mac:
            return Response({"error": "MAC address is required"}, status=400)

        # 1. Buscar o crear el dispositivo por su MAC address
        zona_defecto, _ = ZonaMonitoreo.objects.get_or_create(
            nombre="Playa Principal",
            defaults={
                "descripcion": "Zona turística principal",
                "latitud": Decimal("10.3910"),
                "longitud": Decimal("-75.4794")
            }
        )
        
        dispositivo, created = DispositivoIot.objects.get_or_create(
            mac_address=mac,
            defaults={
                "id_zona": zona_defecto,
                "nombre": f"ESP32-{mac.replace(':', '')[-6:]}",
                "modelo": "ESP32-WROOM-32",
                "firmware_version": "v1.0.0",
                "ip_actual": request.META.get('REMOTE_ADDR', '127.0.0.1'),
                "estado": "ACTIVO",
                "ultima_conexion": timezone.now()
            }
        )
        
        if not created:
            dispositivo.ip_actual = request.META.get('REMOTE_ADDR', dispositivo.ip_actual)
            dispositivo.ultima_conexion = timezone.now()
            dispositivo.save()

        lecturas_data = request.data.get('lecturas', [])
        
        # Si recibimos el formato plano directo de la ESP32, lo estructuramos
        if not lecturas_data:
            mapeo_variables = [
                {"clave": "temperatura", "simbolo": "T", "nombre_var": "Temperatura", "unidad": "°C"},
                {"clave": "humedad", "simbolo": "H", "nombre_var": "Humedad", "unidad": "%"},
                {"clave": "aire", "simbolo": "AQI", "nombre_var": "Calidad del Aire", "unidad": "AQI"},
                {"clave": "uv", "simbolo": "UV", "nombre_var": "Radiacion UV", "unidad": "UV"},
            ]
            for var in mapeo_variables:
                val = request.data.get(var["clave"])
                if val is not None:
                    lecturas_data.append({
                        "simbolo": var["simbolo"],
                        "valor": val,
                        "nombre_var": var["nombre_var"],
                        "unidad": var["unidad"]
                    })
        
        respuestas = []

        for item in lecturas_data:
            simbolo = item.get('simbolo')
            valor = item.get('valor')
            nombre_var = item.get('nombre_var', simbolo)
            unidad = item.get('unidad', '')

            if simbolo is None or valor is None:
                continue

            # Buscar o crear tipo de variable
            tipo_var, _ = TipoVariable.objects.get_or_create(
                simbolo=simbolo,
                defaults={
                    "nombre": nombre_var,
                    "unidad_medida": unidad,
                    "estado": "ACTIVO"
                }
            )

            # Buscar o crear sensor para este dispositivo
            sensor, _ = Sensor.objects.get_or_create(
                id_dispositivo=dispositivo,
                id_tipo_variable=tipo_var,
                defaults={
                    "nombre": f"Sensor {nombre_var} {dispositivo.nombre}",
                    "modelo": f"DHT/MQ/UV-{simbolo}",
                    "pin_conexion": "GPIO",
                    "fecha_instalacion": timezone.now().date(),
                    "estado": "ACTIVO"
                }
            )

            # Crear la lectura
            lectura = LecturaSensor.objects.create(
                id_sensor=sensor,
                id_dispositivo=dispositivo,
                id_tipo_variable=tipo_var,
                valor=Decimal(str(valor))
            )

            # 3. Comprobación automática de alertas basada en umbrales de alerta
            umbrales = UmbralAlerta.objects.filter(id_tipo_variable=tipo_var, activo=True)
            for umbral in umbrales:
                if umbral.valor_minimo <= lectura.valor <= umbral.valor_maximo:
                    estado_amb = umbral.id_estado_ambiental
                    if estado_amb.nombre != "Normal":
                        # Creamos la alerta
                        alerta = Alerta.objects.create(
                            id_lectura=lectura,
                            id_umbral=umbral,
                            id_dispositivo=dispositivo,
                            titulo=f"Alerta de {nombre_var} - Nivel {estado_amb.nombre}",
                            mensaje=f"El sensor {sensor.nombre} registró un valor de {lectura.valor} {tipo_var.unidad_medida}, lo que entra en el nivel {estado_amb.nombre}.",
                            estado="PENDIENTE"
                        )
                        
                        # Activar buzzer si existe
                        buzzer = Buzzer.objects.filter(id_dispositivo=dispositivo).first()
                        if buzzer:
                            buzzer.estado = "ACTIVO"
                            buzzer.save()
                            
                            # Log del cambio de estado del buzzer
                            EstadoBuzzer.objects.create(
                                id_buzzer=buzzer,
                                id_alerta=alerta,
                                estado="ACTIVO",
                                motivo_variacion=f"Activación automática por nivel {estado_amb.nombre} en lectura de {nombre_var} ({lectura.valor})",
                                activador_por="SISTEMA"
                            )

            respuestas.append({
                "simbolo": simbolo,
                "status": "success",
                "lectura_id": lectura.id_lectura
            })

        # Procesar respuesta de comando si la envía el ESP32
        respuesta_data = request.data.get('respuesta_comando')
        if respuesta_data:
            id_comando = respuesta_data.get('id_comando')
            codigo = respuesta_data.get('codigo_respuesta', 'OK')
            msg = respuesta_data.get('mensaje', '')
            exito = respuesta_data.get('exitoso', True)
            try:
                comando = ComandoRemoto.objects.get(id_comando=id_comando)
                # Registrar la respuesta
                RespuestaComando.objects.create(
                    id_comando=comando,
                    codigo_respuesta=codigo,
                    mensaje=msg,
                    exitoso=exito
                )
                
                # Si el comando era cambiar estado del buzzer, reflejarlo en el modelo Buzzer
                if comando.tipo_comando == "BUZZER":
                    state = comando.payload.get("state", "APAGADO")
                    buzzer = Buzzer.objects.filter(id_dispositivo=dispositivo).first()
                    if buzzer:
                        buzzer.estado = state
                        buzzer.save()
                        EstadoBuzzer.objects.create(
                            id_buzzer=buzzer,
                            estado="ACTIVO" if state == "ENCENDIDO" else "INACTIVO",
                            motivo_variacion="Comando remoto ejecutado por ESP32",
                            activador_por="MANUAL"
                        )
            except Exception as e:
                print(f"Error procesando respuesta de comando: {e}", flush=True)

        # Buscar comandos pendientes para este dispositivo (que no tengan respuesta registrada)
        comando_pendiente = ComandoRemoto.objects.filter(
            id_dispositivo=dispositivo
        ).exclude(
            respuestacomando__isnull=False
        ).order_by('fecha_creacion').first()

        response_payload = {
            "status": "success",
            "device": dispositivo.nombre,
            "processed": respuestas
        }

        if comando_pendiente:
            response_payload["comando"] = {
                "id_comando": comando_pendiente.id_comando,
                "tipo_comando": comando_pendiente.tipo_comando,
                "payload": comando_pendiente.payload
            }

        return Response(response_payload, status=201)


class RecuperarPasswordView(APIView):
    """
    Endpoint para restablecer la contraseña si el usuario y correo electrónico coinciden.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not username or not email or not new_password:
            return Response({"error": "Todos los campos son obligatorios"}, status=400)

        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password
        from .models import Usuario

        try:
            # Buscar el usuario oficial
            auth_user = User.objects.get(username=username, email=email)
            
            # Actualizar contraseña en django auth user
            auth_user.password = make_password(new_password)
            auth_user.save()

            # Actualizar contraseña en nuestra tabla personalizada
            try:
                usuario = Usuario.objects.get(idusuarios=auth_user.id)
                usuario.password = new_password
                usuario.save()
            except Usuario.DoesNotExist:
                Usuario.objects.create(
                    idusuarios=auth_user.id,
                    nombre=auth_user.first_name,
                    apellido=auth_user.last_name,
                    username=auth_user.username,
                    password=new_password
                )

            return Response({"message": "Contraseña restablecida exitosamente"}, status=200)

        except User.DoesNotExist:
            return Response({"error": "El usuario o correo electrónico no coinciden"}, status=400)