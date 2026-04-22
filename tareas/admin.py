from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    # Esto hace que la fecha de creación se pueda ver en el panel (por defecto Django la oculta)
    readonly_fields = ("created", )
    
    # Esto crea columnas bonitas en la lista de tareas
    list_display = ('title', 'user', 'important', 'created', 'datecompleted')
    
    # Esto agrega una barra de búsqueda
    search_fields = ('title', 'description')

# Registramos el modelo junto con su nueva configuración
admin.site.register(Task, TaskAdmin)