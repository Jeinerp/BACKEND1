import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    Rol, Recurso, RecursoHasRol, Usuario, UsuarioHasRol,
    ZonaMonitoreo, DispositivoIot, TipoVariable, Sensor,
    LecturaSensor, EstadoAmbiental, UmbralAlerta, Alerta, Buzzer
)

def seed():
    print("Limpiando base de datos...")
    Alerta.objects.all().delete()
    LecturaSensor.objects.all().delete()
    Sensor.objects.all().delete()
    Buzzer.objects.all().delete()
    DispositivoIot.objects.all().delete()
    ZonaMonitoreo.objects.all().delete()
    UmbralAlerta.objects.all().delete()
    TipoVariable.objects.all().delete()
    EstadoAmbiental.objects.all().delete()
    RecursoHasRol.objects.all().delete()
    Recurso.objects.all().delete()
    # No borramos roles ni usuarios para no perder el admin, pero limpiamos sus relaciones
    UsuarioHasRol.objects.all().delete()

    print("Iniciando carga de datos de prueba...")

    # 1. Roles
    admin_role, _ = Rol.objects.get_or_create(nombre="Administrador", defaults={'estado': 1})
    op_role, _ = Rol.objects.get_or_create(nombre="Operador", defaults={'estado': 1})

    # 2. Recursos (Menú)
    recursos_data = [
        ("Dashboard", "/dashboard", "layout-dashboard", 1),
        ("Dispositivos", "/dispositivos", "cpu", 2),
        ("Zonas", "/zonas", "map", 3),
        ("Sensores", "/sensores", "thermometer", 4),
        ("Lecturas", "/lecturas", "database", 5),
        ("Alertas", "/alertas", "alert-triangle", 6),
        ("Actuadores", "/actuadores", "radio", 7),
        ("Usuarios y Roles", "/usuarios", "users", 10),
        ("Auditoría", "/auditoria", "file-text", 11),
    ]
    
    for nom, path, ico, ord in recursos_data:
        rec = Recurso.objects.create(nombre=nom, path=path, icono=ico, orden=ord, estado="activo")
        RecursoHasRol.objects.create(rol_idrol=admin_role, recurso_idrecursos=rec)
        if ord < 8:
            RecursoHasRol.objects.create(rol_idrol=op_role, recurso_idrecursos=rec)

    # 3. Usuario Admin
    user_admin = Usuario.objects.filter(username='admin').first()
    if user_admin:
        UsuarioHasRol.objects.create(usuario_idusuarios=user_admin, rol_idrol=admin_role)

    # 4. Zonas
    zonas_data = [
        ("Playa Norte", "Zona turistica principal", 10.3910, -75.4794),
        ("Muelle Principal", "Area de embarque y carga", 10.3950, -75.4850),
        ("Reserva Coralina", "Zona protegida de monitoreo ambiental", 10.3800, -75.5000)
    ]
    zonas = [ZonaMonitoreo.objects.create(nombre=nom, descripcion=desc, latitud=lat, longitud=lon) for nom, desc, lat, lon in zonas_data]

    # 5. Dispositivos
    disps = []
    for i, z in enumerate(zonas):
        d = DispositivoIot.objects.create(
            nombre=f"Estacion {z.nombre}",
            id_zona=z,
            mac_address=f"AA:BB:CC:DD:EE:0{i}",
            modelo="ESP32-WROOM",
            estado="ACTIVO",
            ip_actual=f"192.168.1.{10+i}"
        )
        disps.append(d)
        Buzzer.objects.create(nombre=f"Buzzer {d.nombre}", id_dispositivo=d, estado="APAGADO")

    # 6. Tipos de Variable
    tv_temp = TipoVariable.objects.create(nombre="Temperatura", unidad_medida="°C", simbolo="°C", estado="ACTIVO")
    tv_hum = TipoVariable.objects.create(nombre="Humedad", unidad_medida="%", simbolo="%", estado="ACTIVO")

    # 7. Estados Ambientales
    est_normal = EstadoAmbiental.objects.create(nombre="Normal", nivel="Bajo", color_referencia="verde", prioridad=1)
    est_critico = EstadoAmbiental.objects.create(nombre="Critico", nivel="Alto", color_referencia="rojo", prioridad=3)

    # 8. Umbrales
    umb_temp = UmbralAlerta.objects.create(id_tipo_variable=tv_temp, id_estado_ambiental=est_critico, valor_minimo=35.0, valor_maximo=100.0, activo=True)

    # 9. Sensores y Lecturas
    print("Generando historial de lecturas...")
    for d in disps:
        s = Sensor.objects.create(
            nombre=f"Temp {d.nombre}", 
            id_dispositivo=d, 
            id_tipo_variable=tv_temp,
            modelo="DS18B20", 
            fecha_instalacion=timezone.now().date(), 
            estado='ACTIVO'
        )
        
        now = timezone.now()
        for h in range(24):
            val = 24.0 + random.uniform(-2, 10)
            lect = LecturaSensor.objects.create(
                id_sensor=s,
                id_dispositivo=d,
                id_tipo_variable=tv_temp,
                valor=round(val, 2),
                fecha_hora=now - timedelta(hours=23-h)
            )
            
            if val > 30:
                Alerta.objects.create(
                    id_dispositivo=d,
                    id_umbral=umb_temp,
                    id_lectura=lect,
                    titulo="Temperatura Alta",
                    mensaje=f"Alerta en {d.nombre}: {round(val,2)}°C",
                    estado="PENDIENTE"
                )

    print("Seed completado con éxito.")

if __name__ == '__main__':
    seed()
