from django.contrib import admin
from .models import (
    Task, UnidadMonetaria, Bingo, Jugador, PartidaBingo, Carton, CartonPartidaBingo, MensajeChat,
    TipoSocio, Socio, CuentaBancaria, MetodoPago, Prestamo, Pago, Ahorro, Regalo, AporteSemanal,
    PlataformaJuego, SesionJuego, ConfiguracionWeb,
)

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

# ==========================================
# REGISTRO DE TABLAS DE SOCIOS / COOPERATIVA
# ==========================================
admin.site.register(TipoSocio)


class SocioAdmin(admin.ModelAdmin):
    list_display = ('idsocio', 'primernombresocio', 'primerapellidosocio', 'cisocio', 'idtiposocio', 'estadosocio')
    search_fields = ('primernombresocio', 'primerapellidosocio', 'cisocio')
    list_filter = ('estadosocio', 'idtiposocio')


admin.site.register(Socio, SocioAdmin)
admin.site.register(CuentaBancaria)
admin.site.register(MetodoPago)


class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('idprestamo', 'idsocio', 'montoprestamosolicitado', 'saldopendiente', 'estadoprestamo')
    list_filter = ('estadoprestamo',)


admin.site.register(Prestamo, PrestamoAdmin)
admin.site.register(Pago)
admin.site.register(Ahorro)
admin.site.register(Regalo)
admin.site.register(AporteSemanal)

# ==========================================
# REGISTRO DE TABLAS DE INFRAESTRUCTURA DE JUEGO
# ==========================================
admin.site.register(PlataformaJuego)
admin.site.register(SesionJuego)
admin.site.register(ConfiguracionWeb)