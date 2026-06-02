from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# ==========================================
# 1. SERIALIZERS DE AUTENTICACIÓN (image_6caa5a.png)
# ==========================================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 1. Datos básicos del usuario
        data['user'] = {
            'username': self.user.username,
            'email': self.user.email,
            'nombre': self.user.first_name or self.user.username,
        }
        
        # 2. Cargar roles asociados al usuario de forma dinámica desde la base de datos
        from .models import Rol, UsuarioHasRol, Recurso, RecursoHasRol
        
        roles_queryset = Rol.objects.filter(usuariohasrol__usuario_idusuarios=self.user, estado=1)
        roles_list = [{'id': r.idrol, 'nombre': r.nombre} for r in roles_queryset]
        
        # Si es superusuario de Django, le garantizamos permisos de Administrador implícitos
        if self.user.is_superuser and not any(r['nombre'] == 'Administrador' for r in roles_list):
            roles_list.append({'id': 1, 'nombre': 'Administrador'})
            
        data['roles'] = roles_list
        
        # 3. Cargar recursos/menús autorizados según los roles del usuario
        if self.user.is_superuser:
            # Superusuarios ven todos los recursos activos
            recursos_queryset = Recurso.objects.filter(estado='activo')
        else:
            # Usuarios normales ven solo los recursos asignados a sus roles
            roles_ids = [r['id'] for r in roles_list]
            recursos_queryset = Recurso.objects.filter(
                recursohasrol__rol_idrol__in=roles_ids, 
                estado='activo'
            ).distinct()
            
        # Ordenamos las opciones del menú por su orden configurado
        recursos_sorted = sorted(
            list(recursos_queryset), 
            key=lambda r: int(r.orden) if r.orden.isdigit() else 99
        )
            
        data['recursos'] = [
            {
                'id': rec.idRecursos,
                'nombre': rec.nombre,
                'path': rec.path,
                'icono': rec.icono,
                'orden': int(rec.orden) if rec.orden.isdigit() else 99
            }
            for rec in recursos_sorted
        ]
        
        return data
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}} # La contraseña no se muestra al consultar

    def create(self, validated_data):
        # Esta línea es la que cifra la contraseña antes de guardarla en la DB
        user = User.objects.create_user(**validated_data)
        return user
    
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['idusuarios', 'nombre', 'apellido', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}} # Ocultar password en las consultas

    def create(self, validated_data):
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password
        
        # 1. Crear en la tabla de autenticación oficial (auth_user)
        auth_user = User.objects.create(
            username=validated_data['username'],
            password=make_password(validated_data['password']),
            first_name=validated_data.get('nombre', ''),
            last_name=validated_data.get('apellido', '')
        )
        
        # 2. Crear en la tabla personalizada con el mismo ID
        usuario = Usuario.objects.create(
            idusuarios=auth_user.id,
            nombre=validated_data.get('nombre', ''),
            apellido=validated_data.get('apellido', ''),
            username=validated_data['username'],
            password=validated_data['password']
        )
        return usuario

    def update(self, instance, validated_data):
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password
        
        # Actualizar en la tabla personalizada
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.password = validated_data['password']
        instance.save()
        
        # Buscar y actualizar en la tabla de autenticación oficial (User)
        try:
            auth_user = User.objects.get(id=instance.idusuarios)
            auth_user.username = instance.username
            auth_user.first_name = instance.nombre
            auth_user.last_name = instance.apellido
            if 'password' in validated_data:
                auth_user.password = make_password(validated_data['password'])
            auth_user.save()
        except User.DoesNotExist:
            User.objects.create(
                id=instance.idusuarios,
                username=instance.username,
                password=make_password(validated_data.get('password', 'default123')),
                first_name=instance.nombre,
                last_name=instance.apellido
            )
            
        return instance

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class RecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurso
        fields = '__all__'

class UsuarioHasRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioHasRol
        fields = '__all__'

class RecursoHasRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecursoHasRol
        fields = '__all__'

# ==========================================
# 2. SERIALIZERS IOT (jeiner_playa_2.png)
# ==========================================

class ZonaMonitoreoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonaMonitoreo
        fields = '__all__'

class DispositivoIotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispositivoIot
        fields = '__all__'

class TipoVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVariable
        fields = '__all__'

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

class LecturaSensorSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para facilitar la visualización en el Frontend
    sensor_nombre = serializers.ReadOnlyField(source='id_sensor.nombre')
    variable_nombre = serializers.ReadOnlyField(source='id_tipo_variable.nombre')
    unidad = serializers.ReadOnlyField(source='id_tipo_variable.unidad_medida')

    class Meta:
        model = LecturaSensor
        fields = '__all__'

class EstadoAmbientalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoAmbiental
        fields = '__all__'

class UmbralAlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UmbralAlerta
        fields = '__all__'

class AlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerta
        fields = '__all__'

class BuzzerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buzzer
        fields = '__all__'

class EstadoBuzzerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoBuzzer
        fields = '__all__'

class ComandoRemotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComandoRemoto
        fields = '__all__'

class RespuestaComandoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaComando
        fields = '__all__'

class AuditoriaSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditoriaSistema
        fields = '__all__'
