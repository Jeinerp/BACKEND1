import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

def initialize():
    print("--- Iniciando Migraciones ---")
    call_command('migrate')
    
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        print("--- Creando Superusuario (admin / admin123) ---")
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    else:
        print("--- El usuario admin ya existe ---")

    print("--- Cargando/actualizando datos de sensores ---")
    try:
        import populate_data
        populate_data.populate()
        print("--- Datos cargados exitosamente ---")
    except Exception as e:
        import traceback
        print(f"Error cargando datos: {e}")
        traceback.print_exc()

    print("--- Inicialización completada con éxito ---")

if __name__ == '__main__':
    initialize()
