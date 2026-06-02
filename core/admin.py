from django.contrib import admin
from .custom_admin import grouped_admin_site
from .models import (
    Usuario, Rol, Recurso, UsuarioHasRol, RecursoHasRol,
    ZonaMonitoreo, DispositivoIot, TipoVariable, Sensor,
    LecturaSensor, EstadoAmbiental, UmbralAlerta, Alerta,
    Buzzer, EstadoBuzzer, ComandoRemoto, RespuestaComando, AuditoriaSistema
)

# Re-registramos los modelos en el nuevo sitio agrupado
@admin.register(ZonaMonitoreo, site=grouped_admin_site)
class ZonaMonitoreoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'latitud', 'longitud', 'fecha_creacion')
    search_fields = ('nombre',)

@admin.register(DispositivoIot, site=grouped_admin_site)
class DispositivoIotAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id_zona', 'mac_address', 'ip_actual', 'estado', 'ultima_conexion')
    list_filter = ('estado', 'id_zona')
    search_fields = ('nombre', 'mac_address')

@admin.register(Sensor, site=grouped_admin_site)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id_dispositivo', 'id_tipo_variable', 'estado')
    list_filter = ('estado', 'id_tipo_variable', 'id_dispositivo')
    search_fields = ('nombre',)

@admin.register(LecturaSensor, site=grouped_admin_site)
class LecturaSensorAdmin(admin.ModelAdmin):
    list_display = ('id_sensor', 'id_tipo_variable', 'valor', 'fecha_hora')
    list_filter = ('id_tipo_variable', 'fecha_hora')
    date_hierarchy = 'fecha_hora'

@admin.register(Alerta, site=grouped_admin_site)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'id_dispositivo', 'estado', 'fecha_generacion')
    list_filter = ('estado', 'fecha_generacion')
    search_fields = ('titulo', 'mensaje')

@admin.register(Buzzer, site=grouped_admin_site)
class BuzzerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id_dispositivo', 'estado')
    list_filter = ('estado',)

@admin.register(Usuario, site=grouped_admin_site)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre', 'apellido')
    search_fields = ('username', 'nombre')

@admin.register(Rol, site=grouped_admin_site)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')

# Registro simple para el resto en el sitio agrupado
grouped_admin_site.register(Recurso)
grouped_admin_site.register(UsuarioHasRol)
grouped_admin_site.register(RecursoHasRol)
grouped_admin_site.register(TipoVariable)
grouped_admin_site.register(EstadoAmbiental)
grouped_admin_site.register(UmbralAlerta)
grouped_admin_site.register(EstadoBuzzer)
grouped_admin_site.register(ComandoRemoto)
grouped_admin_site.register(RespuestaComando)
grouped_admin_site.register(AuditoriaSistema)