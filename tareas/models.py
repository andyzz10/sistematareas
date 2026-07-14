from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator # <- NUEVO IMPORT PARA VALIDAR
import json
import random

# Validador estricto: Solo permite dígitos del 0 al 9
solo_numeros = RegexValidator(regex=r'^\d+$', message='Este campo solo puede contener números, sin letras ni espacios.')

# --- TU MODELO ORIGINAL ---
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + ' - por ' + self.user.username

# --- TRADUCCIÓN DE TU MODELO E-R (BINGO CORE) ---

class UnidadMonetaria(models.Model):
    idunidadmonetaria = models.AutoField(primary_key=True)
    nombremoneda = models.CharField(max_length=100)
    tipomoneda = models.CharField(max_length=12, choices=[('Efectivo', 'Efectivo'), ('Virtual', 'Virtual')])
    simbolomoneda = models.CharField(max_length=255)
    tasaconversionmoneda = models.DecimalField(max_digits=10, decimal_places=2)
    estadomoneda = models.BooleanField(default=True)

class Bingo(models.Model):
    idbingo = models.AutoField(primary_key=True)
    idunidadmonetaria = models.ForeignKey(UnidadMonetaria, on_delete=models.RESTRICT, db_column='idunidadmonetaria')
    titulobingo = models.CharField(max_length=150)
    fechaprogramadabingo = models.DateTimeField()
    tipobingo = models.CharField(max_length=20, choices=[('Virtual', 'Virtual'), ('Presencial', 'Presencial')])
    preciocarton = models.DecimalField(max_digits=10, decimal_places=2)
    premiomayor = models.DecimalField(max_digits=10, decimal_places=2)
    descripcionpremiomayor = models.CharField(max_length=100)
    estadobingo = models.CharField(max_length=20, choices=[('Programado', 'Programado'), ('En Curso', 'En Curso'), ('Finalizado', 'Finalizado')])

class Jugador(models.Model):
    idjugador = models.AutoField(primary_key=True)
    # Vínculo con el User de Django para aprovechar tu login actual
    usuario_django = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombresjugador = models.CharField(max_length=100, null=True, blank=True)
    aliasjugador = models.CharField(max_length=100, unique=True, null=True, blank=True)
    fecharegistrojugador = models.DateTimeField(auto_now_add=True)
    saldocreditojugador = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldovirtualjugador = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estadocuentajugador = models.CharField(max_length=20, default='Activo')
    cedulaidentidadjugador = models.CharField(max_length=10, unique=True, null=True, blank=True, validators=[solo_numeros])
    fecharegistrojugador = models.DateTimeField(auto_now_add=True)
    saldocreditojugador = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldovirtualjugador = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estadocuentajugador = models.CharField(max_length=20, default='Activo')

class PartidaBingo(models.Model):
    idpartidabingo = models.AutoField(primary_key=True)
    # Le agregamos null=True, blank=True para que las partidas antiguas no den error
    idbingo = models.ForeignKey(Bingo, on_delete=models.CASCADE, db_column='idbingo', null=True, blank=True)
    idjugadorganador = models.ForeignKey(Jugador, on_delete=models.SET_NULL, null=True, blank=True, db_column='idjugadorganador')
    # Valores por defecto para que Django llene los datos viejos
    nombreronda = models.CharField(max_length=100, default='Ronda 1')
    modalidadvictoria = models.CharField(max_length=100, default='Cartón Lleno')
    valorpremio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    premiomaterial = models.CharField(max_length=150, default='Ninguno')
    estadopremiomaterial = models.CharField(max_length=20, default='No Aplica')
    estadopartida = models.CharField(max_length=20, default='Programado')
    bolascantadas = models.JSONField(default=list) 
    ultimabola = models.IntegerField(default=0)
    horainicio = models.DateTimeField(auto_now_add=True)

class Carton(models.Model):
    idcarton = models.AutoField(primary_key=True)
    codigocarton = models.CharField(max_length=30, unique=True)
    matriznumeros = models.JSONField() # JSONField reemplaza el CHECK(ISJSON)
    esmaestro = models.BooleanField(default=False)

class CartonPartidaBingo(models.Model):
    idcartonpartida = models.AutoField(primary_key=True)
    idjugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, db_column='idjugador')
    idpartida = models.ForeignKey(PartidaBingo, on_delete=models.CASCADE, db_column='idpartida')
    idcarton = models.ForeignKey(Carton, on_delete=models.CASCADE, db_column='idcarton')
    estadocarton = models.CharField(max_length=20, default='Vendido')
    numerosmarcados = models.JSONField(default=list)
class MensajeChat(models.Model):
    idmensaje = models.AutoField(primary_key=True)
    idbingo = models.ForeignKey(Bingo, on_delete=models.CASCADE, db_column='idbingo')
    usuario = models.CharField(max_length=100)
    mensaje = models.TextField() # Corresponde al varchar(max)
    fechahora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario}: {self.mensaje[:20]}"