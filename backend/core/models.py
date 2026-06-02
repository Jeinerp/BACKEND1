from django.conf import settings
from django.db import models

class Usuario(models.Model):
    idusuarios = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45)
    apellido = models.CharField(max_length=45)
    username = models.CharField(max_length=45, unique=True)
    password = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.username})"

    class Meta:
        db_table = 'usuario'
        verbose_name = "Usuario"
        verbose_name_plural = "01. Usuarios del Sistema"

class Rol(models.Model):
    idrol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45)
    estado = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'rol'
        verbose_name = "Rol"
        verbose_name_plural = "02. Roles"

class Recurso(models.Model):
    idRecursos = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45)
    url_backend = models.CharField(max_length=45, blank=True, null=True)
    url_frontend = models.CharField(max_length=45, blank=True, null=True)
    path = models.CharField(max_length=45)
    icono = models.CharField(max_length=45, blank=True, null=True)
    orden = models.CharField(max_length=45)
    recurso_padre = models.CharField(max_length=45, blank=True, null=True)
    estado = models.CharField(max_length=45, default='activo')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'recurso'
        verbose_name = "Recurso"
        verbose_name_plural = "03. Recursos (URLs)"

class UsuarioHasRol(models.Model):
    # CAMBIO CLAVE: Ahora apunta a settings.AUTH_USER_MODEL (la tabla de arriba en el admin)
    usuario_idusuarios = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        db_column='usuario_idusuarios'
    )
    rol_idrol = models.ForeignKey(
        'Rol', 
        on_delete=models.CASCADE, 
        db_column='rol_idrol'
    )

    def __str__(self):
        # Usamos .username porque es un campo estándar del modelo oficial
        return f"{self.usuario_idusuarios.username} - {self.rol_idrol.nombre}"

    class Meta:
        db_table = 'usuario_has_rol'
        verbose_name = "Asignación de Rol"
        verbose_name_plural = "04. Usuarios con Roles"
        unique_together = (('usuario_idusuarios', 'rol_idrol'),)

class RecursoHasRol(models.Model):
    recurso_idrecursos = models.ForeignKey(Recurso, on_delete=models.CASCADE, db_column='recurso_idrecursos')
    rol_idrol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='rol_idrol')

    def __str__(self):
        return f"{self.rol_idrol.nombre} tiene acceso a {self.recurso_idrecursos.nombre}"

    class Meta:
        db_table = 'recurso_has_rol'
        verbose_name = "Permiso de Recurso"
        verbose_name_plural = "05. Permisos por Rol"
        unique_together = (('recurso_idrecursos', 'rol_idrol'),)

class ZonaMonitoreo(models.Model):
    id_zona = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7)
    longitud = models.DecimalField(max_digits=10, decimal_places=7)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'zona_monitoreo'
        verbose_name = "Zona de Monitoreo"
        verbose_name_plural = "06. Zonas de Monitoreo"

class DispositivoIot(models.Model):
    id_dispositivo = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(ZonaMonitoreo, on_delete=models.CASCADE, db_column='id_zona')
    nombre = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=50, unique=True)
    modelo = models.CharField(max_length=80)
    firmware_version = models.CharField(max_length=50)
    ip_actual = models.GenericIPAddressField()
    estado = models.CharField(max_length=20, default='ACTIVO')
    ultima_conexion = models.DateTimeField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.mac_address})"

    class Meta:
        db_table = 'dispositivo_iot'
        verbose_name = "Dispositivo IoT"
        verbose_name_plural = "07. Dispositivos IoT"

class TipoVariable(models.Model):
    id_tipo_variable = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    unidad_medida = models.CharField(max_length=20)
    simbolo = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=20, default='ACTIVO')

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"

    class Meta:
        db_table = 'tipo_variable'
        verbose_name = "Tipo de Variable"
        verbose_name_plural = "08. Tipos de Variables"

class Sensor(models.Model):
    id_sensor = models.AutoField(primary_key=True)
    id_dispositivo = models.ForeignKey(DispositivoIot, on_delete=models.CASCADE, db_column='id_dispositivo')
    id_tipo_variable = models.ForeignKey(TipoVariable, on_delete=models.CASCADE, db_column='id_tipo_variable')
    nombre = models.CharField(max_length=100)
    modelo = models.CharField(max_length=80)
    pin_conexion = models.CharField(max_length=20)
    estado = models.CharField(max_length=20, default='ACTIVO')
    fecha_instalacion = models.DateField()

    def __str__(self):
        return f"{self.nombre} en {self.id_dispositivo.nombre}"

    class Meta:
        db_table = 'sensor'
        verbose_name = "Sensor"
        verbose_name_plural = "09. Sensores"

class LecturaSensor(models.Model):
    id_lectura = models.BigAutoField(primary_key=True)
    id_sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, db_column='id_sensor')
    id_dispositivo = models.ForeignKey(DispositivoIot, on_delete=models.CASCADE, db_column='id_dispositivo')
    id_tipo_variable = models.ForeignKey(TipoVariable, on_delete=models.CASCADE, db_column='id_tipo_variable')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lectura {self.id_tipo_variable.nombre}: {self.valor} ({self.fecha_hora})"

    class Meta:
        db_table = 'lectura_sensor'
        verbose_name = "Lectura de Sensor"
        verbose_name_plural = "10. Histórico de Lecturas"

class EstadoAmbiental(models.Model):
    id_estado_ambiental = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    nivel = models.CharField(max_length=20)
    color_referencia = models.CharField(max_length=30)
    prioridad = models.IntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'estado_ambiental'
        verbose_name = "Estado Ambiental"
        verbose_name_plural = "11. Estados Ambientales"

class UmbralAlerta(models.Model):
    id_umbral = models.AutoField(primary_key=True)
    id_tipo_variable = models.ForeignKey(TipoVariable, on_delete=models.CASCADE, db_column='id_tipo_variable')
    id_estado_ambiental = models.ForeignKey(EstadoAmbiental, on_delete=models.CASCADE, db_column='id_estado_ambiental')
    valor_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    valor_maximo = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Umbral {self.id_tipo_variable.nombre} - {self.id_estado_ambiental.nombre}"

    class Meta:
        db_table = 'umbral_alerta'
        verbose_name = "Umbral de Alerta"
        verbose_name_plural = "12. Umbrales de Alertas"

class Alerta(models.Model):
    id_alerta = models.BigAutoField(primary_key=True)
    id_lectura = models.ForeignKey(LecturaSensor, on_delete=models.CASCADE, db_column='id_lectura')
    id_umbral = models.ForeignKey(UmbralAlerta, on_delete=models.CASCADE, db_column='id_umbral')
    id_dispositivo = models.ForeignKey(DispositivoIot, on_delete=models.CASCADE, db_column='id_dispositivo')
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    estado = models.CharField(max_length=20, default='PENDIENTE')
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'alerta'
        verbose_name = "Alerta"
        verbose_name_plural = "13. Alertas Generadas"

class Buzzer(models.Model):
    id_buzzer = models.AutoField(primary_key=True)
    id_dispositivo = models.ForeignKey(DispositivoIot, on_delete=models.CASCADE, db_column='id_dispositivo')
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, default='APAGADO')

    def __str__(self):
        return f"Buzzer {self.nombre} ({self.id_dispositivo.nombre})"

    class Meta:
        db_table = 'buzzer'
        verbose_name = "Buzzer"
        verbose_name_plural = "14. Buzzers (Alarmas)"

class ComandoRemoto(models.Model):
    id_comando = models.BigAutoField(primary_key=True)
    id_dispositivo = models.ForeignKey(DispositivoIot, on_delete=models.CASCADE, db_column='id_dispositivo')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    tipo_comando = models.CharField(max_length=20)
    payload = models.JSONField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comando {self.tipo_comando} a {self.id_dispositivo.nombre}"

    class Meta:
        db_table = 'comando_remoto'
        verbose_name = "Comando Remoto"
        verbose_name_plural = "15. Comandos Enviados"

class AuditoriaSistema(models.Model):
    id_auditoria = models.BigAutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, db_column='id_usuario')
    accion = models.CharField(max_length=100)
    tabla_afectada = models.CharField(max_length=100)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accion} en {self.tabla_afectada} ({self.fecha_hora})"

    class Meta:
        db_table = 'auditoria_sistema'
        verbose_name = "Auditoría"
        verbose_name_plural = "16. Logs de Auditoría"

class EstadoBuzzer(models.Model):
    id_estado_buzzer = models.BigAutoField(primary_key=True)
    id_buzzer = models.ForeignKey('Buzzer', on_delete=models.CASCADE, db_column='id_buzzer')
    id_alerta = models.ForeignKey('Alerta', on_delete=models.SET_NULL, null=True, db_column='id_alerta')
    estado = models.CharField(max_length=20) # ACTIVO / INACTIVO
    motivo_variacion = models.CharField(max_length=255, blank=True, null=True)
    activado_por = models.CharField(max_length=50) # SISTEMA / MANUAL
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Estado Buzzer: {self.estado} ({self.fecha_hora})"

    class Meta:
        db_table = 'estado_buzzer'
        verbose_name = "Estado de Buzzer"
        verbose_name_plural = "17. Estados de Buzzers (Historial)"

class RespuestaComando(models.Model):
    id_respuesta = models.BigAutoField(primary_key=True)
    id_comando = models.ForeignKey('ComandoRemoto', on_delete=models.CASCADE, db_column='id_comando')
    codigo_respuesta = models.CharField(max_length=50)
    mensaje = models.TextField()
    exitoso = models.BooleanField(default=True)
    respuesta_json = models.JSONField(blank=True, null=True)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta ID: {self.id_respuesta} (Éxito: {self.exitoso})"

    class Meta:
        db_table = 'respuesta_comando'
        verbose_name = "Respuesta de Comando"
        verbose_name_plural = "18. Respuestas de Dispositivos"
