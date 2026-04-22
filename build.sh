#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Correr migraciones
python manage.py migrate
# Crear superusuario de forma no interactiva (Truco para el plan gratis)
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='tu_usuario').exists() or User.objects.create_superuser('Andyz15', 'admin@example.com', '13080907')"