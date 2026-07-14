from django.contrib import admin
from django.urls import path
from tareas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de Autenticación e Inicio
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    
    # Rutas del Bingo Virtual
    path('bingo/', views.bingo_lobby, name='bingo_lobby'),
    path('bingo/<int:idpartidabingo>/', views.bingo_view, name='bingo'),
    path('api/bingo/<int:idpartidabingo>/estado/', views.api_estado_partida, name='bingo_estado'),
    path('api/bingo/<int:idpartidabingo>/sacar/', views.api_sacar_balota, name='api_sacar_balota'),
    path('api/bingo/<int:idbingo>/mensajes/obtener/', views.api_obtener_mensajes, name='api_obtener_mensajes'),
    path('api/bingo/<int:idbingo>/mensajes/enviar/', views.api_enviar_mensaje, name='api_enviar_mensaje'),
]