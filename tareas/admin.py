from django.contrib import admin
from .models import Task, UnidadMonetaria, Bingo, Jugador, PartidaBingo, Carton, CartonPartidaBingo, MensajeChat

# Configuración de tu tabla de tareas original
class TaskAdmin(admin.ModelAdmin):
    # Esto hace que la fecha de creación se pueda ver en el panel
    readonly_fields = ("created", )
    # Esto crea columnas bonitas en la lista de tareas
    list_display = ('title', 'user', 'important', 'created', 'datecompleted')
    # Esto agrega una barra de búsqueda
    search_fields = ('title', 'description')

admin.site.register(Task, TaskAdmin)

# ==========================================
# REGISTRO DE TABLAS DEL BINGO
# ==========================================
admin.site.register(UnidadMonetaria)
admin.site.register(Bingo)
admin.site.register(Jugador)
admin.site.register(PartidaBingo)
admin.site.register(Carton)
admin.site.register(CartonPartidaBingo)
admin.site.register(MensajeChat)