from django.contrib import admin
from django.apps import apps

class GroupedAdminSite(admin.AdminSite):
    site_header = "Administración de HydroSmart IoT"
    site_title = "HydroSmart IoT Portal"
    index_title = "Gestión del Sistema"

    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request)
        
        # Definimos nuestras categorías personalizadas
        # El nombre debe coincidir con el nombre de la clase del modelo
        groups = {
            'SEGURIDAD Y ACCESO': [
                'Usuario', 'Rol', 'Recurso', 'UsuarioHasRol', 'RecursoHasRol', 'Group', 'User'
            ],
            'INFRAESTRUCTURA IOT': [
                'ZonaMonitoreo', 'DispositivoIot'
            ],
            'SENSORES Y TELEMETRÍA': [
                'Sensor', 'TipoVariable', 'LecturaSensor', 'EstadoAmbiental'
            ],
            'CONTROL Y ALERTAS': [
                'Alerta', 'UmbralAlerta', 'Buzzer', 'EstadoBuzzer', 'ComandoRemoto', 'RespuestaComando'
            ],
            'SISTEMA Y AUDITORÍA': [
                'AuditoriaSistema'
            ]
        }

        new_app_list = []
        
        # Mapeamos los modelos originales a nuestras categorías
        for group_name, model_names in groups.items():
            group_models = []
            for app in app_dict.values():
                for model in app['models']:
                    if model['object_name'] in model_names:
                        group_models.append(model)
            
            if group_models:
                # Ordenar modelos alfabéticamente dentro del grupo si se desea
                group_models.sort(key=lambda x: x['name'])
                new_app_list.append({
                    'name': group_name,
                    'app_label': group_name.lower().replace(' ', '_'),
                    'models': group_models,
                })
        
        return new_app_list

# Instanciamos el sitio personalizado
grouped_admin_site = GroupedAdminSite(name='grouped_admin')
