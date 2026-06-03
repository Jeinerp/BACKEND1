import os
import django
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    ZonaMonitoreo, DispositivoIot, TipoVariable, Sensor, 
    LecturaSensor, EstadoAmbiental, UmbralAlerta, Alerta, Buzzer,
    Rol, UsuarioHasRol, Recurso
)
from django.contrib.auth import get_user_model

User = get_user_model()

def populate():
    print("Starting data population...")

    # 1. Zonas
    zonas_data = [
        {"nombre": "Playa Principal", "descripcion": "Zona turística principal", "lat": 10.3910, "lon": -75.4794},
        {"nombre": "Reserva Natural", "descripcion": "Área protegida de manglares", "lat": 10.4201, "lon": -75.5210},
        {"nombre": "Zona Hotelera", "descripcion": "Sector de alta densidad poblacional", "lat": 10.3850, "lon": -75.4900},
    ]
    
    zonas = []
    for z in zonas_data:
        zona, created = ZonaMonitoreo.objects.get_or_create(
            nombre=z["nombre"],
            defaults={
                "descripcion": z["descripcion"],
                "latitud": Decimal(str(z["lat"])),
                "longitud": Decimal(str(z["lon"]))
            }
        )
        zonas.append(zona)
    print(f"Created/found {len(zonas)} zones.")

    # 2. Tipos de Variable
    variables_data = [
        {"nombre": "Temperatura", "unidad": "°C", "simbolo": "T"},
        {"nombre": "Humedad", "unidad": "%", "simbolo": "H"},
        {"nombre": "Nivel de Agua", "unidad": "m", "simbolo": "W"},
        {"nombre": "Calidad del Aire", "unidad": "AQI", "simbolo": "AQI"},
    ]
    
    variables = []
    for v in variables_data:
        var, created = TipoVariable.objects.get_or_create(
            nombre=v["nombre"],
            defaults={"unidad_medida": v["unidad"], "simbolo": v["simbolo"]}
        )
        variables.append(var)
    print(f"Created/found {len(variables)} variables.")

    # 3. Estados Ambientales
    estados_data = [
        {"nombre": "Normal", "nivel": "BAJO", "color": "#10b981", "prioridad": 1},
        {"nombre": "Precaución", "nivel": "MEDIO", "color": "#f59e0b", "prioridad": 2},
        {"nombre": "Alerta", "nivel": "ALTO", "color": "#ef4444", "prioridad": 3},
        {"nombre": "Crítico", "nivel": "CRÍTICO", "color": "#7f1d1d", "prioridad": 4},
    ]
    
    estados = []
    for e in estados_data:
        est, created = EstadoAmbiental.objects.get_or_create(
            nombre=e["nombre"],
            defaults={"nivel": e["nivel"], "color_referencia": e["color"], "prioridad": e["prioridad"]}
        )
        estados.append(est)
    print(f"Created/found {len(estados)} environmental states.")

    # 4. Dispositivos e Sensores
    dispositivos = []
    for i, zona in enumerate(zonas):
        disp, created = DispositivoIot.objects.get_or_create(
            mac_address=f"00:1B:44:11:3A:0{i}",
            defaults={
                "id_zona": zona,
                "nombre": f"Nodo-{zona.nombre.split()[0]}",
                "modelo": "ESP32-WROOM-32",
                "firmware_version": "v2.1.0",
                "ip_actual": f"192.168.1.{10 + i}",
                "estado": "ACTIVO",
                "ultima_conexion": datetime.now()
            }
        )
        dispositivos.append(disp)
        
        # Add Sensors to device
        for var in variables:
            Sensor.objects.get_or_create(
                id_dispositivo=disp,
                id_tipo_variable=var,
                defaults={
                    "nombre": f"Sensor {var.nombre} {disp.nombre}",
                    "modelo": f"MOD-{var.simbolo}-99",
                    "pin_conexion": "A0",
                    "fecha_instalacion": datetime.now().date()
                }
            )
            
        # Add Buzzer
        Buzzer.objects.get_or_create(
            id_dispositivo=disp,
            nombre=f"Alarma Sonora {disp.nombre}",
            defaults={"estado": "APAGADO"}
        )

    print(f"Created/found {len(dispositivos)} devices with sensors and buzzers.")

    # 5. Lecturas (Generate historical data for all sensor types)
    print("Generating sensor readings for ALL variable types...")
    sensors = Sensor.objects.all()
    now = datetime.now()
    readings_count = 0
    
    for sensor in sensors:
        existing = LecturaSensor.objects.filter(id_sensor=sensor).count()
        if existing >= 40:
            print(f"  Sensor '{sensor.nombre}' ya tiene {existing} lecturas, saltando.")
            continue
        
        var_name = sensor.id_tipo_variable.nombre
        # Realistic base values per variable type
        if var_name == "Temperatura":
            base_val = 28  # Tropical beach temperature
        elif var_name == "Humedad":
            base_val = 72  # Coastal humidity
        elif var_name == "Nivel de Agua":
            base_val = 1.8  # Sea level in meters
        elif var_name == "Calidad del Aire":
            base_val = 42  # Moderate AQI
        else:
            base_val = 50
        
        # Range of variation per type
        variation = 5 if var_name != "Nivel de Agua" else 0.8
        
        print(f"  Generando lecturas para: {sensor.nombre} ({var_name})...")
        for h in range(48):  # 48 hours of data
            time = now - timedelta(hours=h)
            val = base_val + random.uniform(-variation, variation)
            if var_name == "Nivel de Agua":
                val = max(0.2, val)  # Can't be negative
            
            LecturaSensor.objects.create(
                id_sensor=sensor,
                id_dispositivo=sensor.id_dispositivo,
                id_tipo_variable=sensor.id_tipo_variable,
                valor=Decimal(f"{val:.2f}"),
                fecha_hora=time
            )
            readings_count += 1
            
    print(f"Generated {readings_count} sensor readings across all variables.")

    # 6. Umbrales
    for var in variables:
        for est in estados:
            min_v = 0
            max_v = 100
            if est.nombre == "Normal": min_v, max_v = 0, 30
            elif est.nombre == "Precaución": min_v, max_v = 31, 60
            elif est.nombre == "Alerta": min_v, max_v = 61, 80
            else: min_v, max_v = 81, 100
            
            UmbralAlerta.objects.get_or_create(
                id_tipo_variable=var,
                id_estado_ambiental=est,
                defaults={"valor_minimo": Decimal(str(min_v)), "valor_maximo": Decimal(str(max_v))}
            )

    # 7. Alertas Recientes
    if Alerta.objects.count() < 5:
        print("Generating alerts...")
        some_lecturas = LecturaSensor.objects.order_by('-fecha_hora')[:5]
        umbral = UmbralAlerta.objects.first()
        for i, lec in enumerate(some_lecturas):
            Alerta.objects.create(
                id_lectura=lec,
                id_umbral=umbral,
                id_dispositivo=lec.id_dispositivo,
                titulo=f"Alerta de {lec.id_tipo_variable.nombre} detectada",
                mensaje=f"Se ha detectado un valor de {lec.valor} {lec.id_tipo_variable.unidad_medida} en {lec.id_dispositivo.nombre}.",
                estado="PENDIENTE" if i % 2 == 0 else "RESUELTA",
                fecha_generacion=lec.fecha_hora
            )

    print("Data population completed successfully!")

    # 6. Roles y Usuarios
    print("Configurando roles por defecto...")
    admin_rol, _ = Rol.objects.get_or_create(nombre='Administrador', defaults={'estado': 1})
    user_rol, _ = Rol.objects.get_or_create(nombre='Usuario Normal', defaults={'estado': 1})

    try:
        admin_user = User.objects.get(username='admin')
        UsuarioHasRol.objects.get_or_create(
            usuario_idusuarios=admin_user,
            rol_idrol=admin_rol
        )
    except User.DoesNotExist:
        pass
    print("Roles configurados correctamente.")

    # 7. Recursos (Menú)
    print("Configurando recursos y permisos por defecto...")
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
    
    from core.models import RecursoHasRol
    for nom, path, ico, ord in recursos_data:
        rec, _ = Recurso.objects.get_or_create(
            nombre=nom, 
            defaults={"path": path, "icono": ico, "orden": ord, "estado": "activo"}
        )
        RecursoHasRol.objects.get_or_create(rol_idrol=admin_rol, recurso_idrecursos=rec)
        if ord < 8:
            RecursoHasRol.objects.get_or_create(rol_idrol=user_rol, recurso_idrecursos=rec)
    print("Recursos configurados correctamente.")

if __name__ == '__main__':
    populate()
