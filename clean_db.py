import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    LecturaSensor, Alerta, EstadoBuzzer, RespuestaComando,
    ComandoRemoto, AuditoriaSistema, Sensor, DispositivoIot,
    ZonaMonitoreo
)

def clean():
    print("--- Limpiando lecturas, alertas, sensores y dispositivos (Simulaciones) ---")
    LecturaSensor.objects.all().delete()
    Alerta.objects.all().delete()
    EstadoBuzzer.objects.all().delete()
    RespuestaComando.objects.all().delete()
    ComandoRemoto.objects.all().delete()
    AuditoriaSistema.objects.all().delete()
    Sensor.objects.all().delete()
    DispositivoIot.objects.all().delete()
    ZonaMonitoreo.objects.all().delete()
    print("--- Base de datos limpia. Lista para recibir datos reales del ESP32 ---")

if __name__ == '__main__':
    clean()
