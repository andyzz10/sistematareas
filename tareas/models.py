from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator # <- NUEVO IMPORT PARA VALIDAR
import json
import random
from .bingo_patterns import MODALIDAD_CHOICES
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
    haydesempate = models.BooleanField(default=False)
    idpartidabingo = models.AutoField(primary_key=True)
    # Le agregamos null=True, blank=True para que las partidas antiguas no den error
    idbingo = models.ForeignKey(Bingo, on_delete=models.CASCADE, db_column='idbingo', null=True, blank=True)
    idjugadorganador = models.ForeignKey(Jugador, on_delete=models.SET_NULL, null=True, blank=True, db_column='idjugadorganador')
    # Valores por defecto para que Django llene los datos viejos
    nombreronda = models.CharField(max_length=100, default='Ronda 1')
    modalidadvictoria = models.CharField(max_length=100, choices=MODALIDAD_CHOICES, default='Tabla Llena')
    valorpremio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    premiomaterial = models.CharField(max_length=150, default='Ninguno')
    estadopremiomaterial = models.CharField(max_length=20, default='No Aplica')
    estadopartida = models.CharField(max_length=20, default='Programado')
    bolascantadas = models.JSONField(default=list) 
    ultimabola = models.IntegerField(default=0)
    # Nuevos campos del modelo E-R que faltaban, necesarios para el desempate
    haydesempate = models.BooleanField(default=False)
    idbingadores = models.JSONField(default=list, blank=True)  # ids de CartonPartidaBingo ganadores (empate)
    bolamayordesempate = models.IntegerField(null=True, blank=True)
    horainicio = models.DateTimeField(auto_now_add=True)
    horafin = models.DateTimeField(null=True, blank=True)

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
    # Campos del modelo E-R que faltaban, necesarios para detectar ganador
    esganador = models.BooleanField(default=False)
    cantidadaciertos = models.IntegerField(default=0)
    fechaganador = models.DateTimeField(null=True, blank=True)
    preciopagado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fechacompra = models.DateTimeField(auto_now_add=True, null=True, blank=True)
class MensajeChat(models.Model):
    idmensaje = models.AutoField(primary_key=True)
    idbingo = models.ForeignKey(Bingo, on_delete=models.CASCADE, db_column='idbingo')
    usuario = models.CharField(max_length=100)
    mensaje = models.TextField() # Corresponde al varchar(max)
    fechahora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario}: {self.mensaje[:20]}"


# ==========================================
# BLOQUE SOCIOS / COOPERATIVA (modelo E-R)
# ==========================================

class TipoSocio(models.Model):
    idtiposocio = models.AutoField(primary_key=True)
    nombretiposocio = models.CharField(max_length=100, unique=True)
    roltiposocio = models.CharField(max_length=50, unique=True)
    descripciondetiposocio = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.nombretiposocio


class Socio(models.Model):
    SEXO_CHOICES = [('H', 'Hombre'), ('M', 'Mujer')]
    ESTADO_CHOICES = [('Activo', 'Activo'), ('Inactivo', 'Inactivo')]

    idsocio = models.AutoField(primary_key=True)
    idtiposocio = models.ForeignKey(TipoSocio, on_delete=models.RESTRICT, db_column='idtiposocio', related_name='socios')
    primernombresocio = models.CharField(max_length=40)
    segundonombresocio = models.CharField(max_length=40, null=True, blank=True)
    primerapellidosocio = models.CharField(max_length=40)
    segundoapellidosocio = models.CharField(max_length=40)
    # Nota: el Excel nombra la columna "cisiocio" pero el constraint de unicidad dice "cisocio".
    # Se usa "cisocio" (cédula de identidad) porque es lo que tiene sentido semánticamente.
    cisocio = models.CharField(max_length=10, unique=True, validators=[solo_numeros])
    fotosocio = models.CharField(max_length=255, null=True, blank=True)
    fechanacimientosocio = models.DateField()
    telefonopersonalsocio = models.CharField(max_length=10, validators=[solo_numeros])
    telefonotrabajosocio = models.CharField(max_length=25, null=True, blank=True)
    direcciondomiciliosocio = models.CharField(max_length=255)
    direcciontrabajosocio = models.CharField(max_length=255, null=True, blank=True)
    sexosocio = models.CharField(max_length=1, choices=SEXO_CHOICES, null=True, blank=True)
    estadosocio = models.CharField(max_length=10, choices=ESTADO_CHOICES)

    def __str__(self):
        return f"{self.primernombresocio} {self.primerapellidosocio}"


class CuentaBancaria(models.Model):
    TIPO_CHOICES = [('Ahorro', 'Ahorro'), ('Corriente', 'Corriente')]
    ESTADO_CHOICES = [('Activa', 'Activa'), ('Inactiva', 'Inactiva')]

    idcuentabancaria = models.AutoField(primary_key=True)
    idsocio = models.ForeignKey(Socio, on_delete=models.CASCADE, db_column='idsocio', related_name='cuentas_bancarias')
    nombrebanco = models.CharField(max_length=100)
    numerocuenta = models.CharField(max_length=30, unique=True)
    tipocuenta = models.CharField(max_length=20, choices=TIPO_CHOICES)
    # Nota: el Excel marca "esprincipal" como unique(esprincipal), lo cual en la práctica
    # solo dejaría UNA cuenta principal en todo el sistema (probable error del modelo E-R).
    # Aquí se deja como booleano normal y la regla real (una principal por socio) se valida en clean().
    esprincipal = models.BooleanField(default=False)
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estadocuenta = models.CharField(max_length=10, choices=ESTADO_CHOICES)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Regla del Excel: "no podrán asociar más de dos cuentas bancarias" (trigger AFTER INSERT)
        qs = CuentaBancaria.objects.filter(idsocio=self.idsocio).exclude(pk=self.pk)
        if qs.count() >= 2:
            raise ValidationError('Este socio ya tiene 2 cuentas bancarias registradas (máximo permitido).')
        # Regla implícita: solo una cuenta principal por socio
        if self.esprincipal and qs.filter(esprincipal=True).exists():
            raise ValidationError('Este socio ya tiene una cuenta bancaria marcada como principal.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombrebanco} - {self.numerocuenta}"


class MetodoPago(models.Model):
    ESTADO_CHOICES = [('Activo', 'Activo'), ('Inactivo', 'Inactivo')]

    idmetodopago = models.AutoField(primary_key=True)
    nombremetodopago = models.CharField(max_length=50, unique=True)
    descripcionmetodopago = models.CharField(max_length=200, null=True, blank=True)
    estadometodopago = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    urlmetodopago = models.CharField(max_length=255)

    def __str__(self):
        return self.nombremetodopago


class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('Solicitado', 'Solicitado'), ('Aprobado', 'Aprobado'),
        ('En espera', 'En espera'), ('Liquidado', 'Liquidado'),
    ]

    idprestamo = models.AutoField(primary_key=True)
    idsocio = models.ForeignKey(Socio, on_delete=models.RESTRICT, db_column='idsocio', related_name='prestamos')
    idgarante1 = models.ForeignKey(Socio, on_delete=models.SET_NULL, null=True, blank=True, db_column='idgarante1', related_name='prestamos_garante1')
    idgarante2 = models.ForeignKey(Socio, on_delete=models.SET_NULL, null=True, blank=True, db_column='idgarante2', related_name='prestamos_garante2')
    montoprestamosolicitado = models.DecimalField(max_digits=12, decimal_places=2)
    tasainteres = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    montototalpagar = models.DecimalField(max_digits=12, decimal_places=2)
    saldopendiente = models.DecimalField(max_digits=12, decimal_places=2)
    numerocuotas = models.PositiveIntegerField(default=1)
    fechasolicitud = models.DateField()
    fechavencimiento = models.DateField()
    estadoprestamo = models.CharField(max_length=20, choices=ESTADO_CHOICES)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.montoprestamosolicitado is not None and self.montoprestamosolicitado <= 0:
            raise ValidationError('El monto solicitado debe ser mayor a 0.')
        if self.numerocuotas is not None and self.numerocuotas < 1:
            raise ValidationError('El número de cuotas debe ser al menos 1.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Préstamo #{self.idprestamo} - {self.idsocio}"


class Pago(models.Model):
    ESTADO_CHOICES = [('Pendiente', 'Pendiente'), ('Validado', 'Validado'), ('Rechazado', 'Rechazado')]

    idpago = models.AutoField(primary_key=True)
    idprestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, db_column='idprestamo', related_name='pagos')
    idmetodopago = models.ForeignKey(MetodoPago, on_delete=models.RESTRICT, db_column='idmetodopago', related_name='pagos')
    montopagado = models.DecimalField(max_digits=10, decimal_places=2)
    numeroreferencia = models.CharField(max_length=50, unique=True, null=True, blank=True)
    fechapago = models.DateTimeField()
    fechaconfirmacionadmin = models.DateTimeField(null=True, blank=True)
    comprobantepago = models.CharField(max_length=255)
    estadopago = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.montopagado is not None and self.montopagado <= 0:
            raise ValidationError('El monto pagado debe ser mayor a 0.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago #{self.idpago} - {self.montopagado}"


class Ahorro(models.Model):
    TIPO_CHOICES = [('Obligatorio', 'Obligatorio'), ('Voluntario', 'Voluntario')]
    ESTADO_CHOICES = [('Activo', 'Activo'), ('Inactivo', 'Inactivo')]

    idahorro = models.AutoField(primary_key=True)
    idsocio = models.ForeignKey(Socio, on_delete=models.CASCADE, db_column='idsocio', related_name='ahorros')
    idbingo = models.ForeignKey(Bingo, on_delete=models.CASCADE, db_column='idbingo', related_name='ahorros')
    tipoahorro = models.CharField(max_length=50, choices=TIPO_CHOICES)
    montoahorro = models.DecimalField(max_digits=10, decimal_places=2)
    fechaahorro = models.DateTimeField()
    comentarioahorro = models.CharField(max_length=100, null=True, blank=True)
    estadoahorro = models.CharField(max_length=25, choices=ESTADO_CHOICES)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.montoahorro is not None and self.montoahorro <= 0:
            raise ValidationError('El monto del ahorro debe ser mayor a 0.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ahorro #{self.idahorro} - {self.idsocio}"


class Regalo(models.Model):
    ESTADO_CHOICES = [('Acumulado', 'Acumulado'), ('Sorteado', 'Sorteado'), ('Entregado', 'Entregado')]

    idregalo = models.AutoField(primary_key=True)
    nombreregalo = models.CharField(max_length=100)
    descripcionregalo = models.CharField(max_length=200, null=True, blank=True)
    valorregalo = models.DecimalField(max_digits=10, decimal_places=2)
    fechaentregaregalo = models.DateTimeField()
    estadoregalo = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fechaultimaactualizacion = models.DateTimeField(null=True, blank=True)
    urlimagen = models.CharField(max_length=255)

    def __str__(self):
        return self.nombreregalo


class AporteSemanal(models.Model):
    METODO_CHOICES = [('Efectivo', 'Efectivo'), ('Transferencia', 'Transferencia'), ('Fisico', 'Fisico')]
    ESTADO_CHOICES = [('Al Dia', 'Al Dia'), ('Atrasado', 'Atrasado')]

    idaporte = models.AutoField(primary_key=True)
    idsocio = models.ForeignKey(Socio, on_delete=models.CASCADE, db_column='idsocio', related_name='aportes_semanales')
    idregalo = models.ForeignKey(Regalo, on_delete=models.RESTRICT, db_column='idregalo', related_name='aportes_semanales')
    idbingo = models.ForeignKey(Bingo, on_delete=models.SET_NULL, null=True, blank=True, db_column='idbingo', related_name='aportes_semanales')
    numerosemana = models.IntegerField(null=True, blank=True)
    fechaplanificadada = models.DateTimeField()
    fechaentregareal = models.DateTimeField(null=True, blank=True)
    metodoingreso = models.CharField(max_length=50, choices=METODO_CHOICES)
    referenciaingreso = models.CharField(max_length=100, null=True, blank=True)
    estadoaporte = models.CharField(max_length=20, choices=ESTADO_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Aporte #{self.idaporte} - {self.idsocio}"


# ==========================================
# BLOQUE INFRAESTRUCTURA DE JUEGO (modelo E-R)
# ==========================================

class PlataformaJuego(models.Model):
    idplataformajuego = models.AutoField(primary_key=True)
    nombreplataforma = models.CharField(max_length=25, unique=True)
    logoplataforma = models.CharField(max_length=255, null=True, blank=True)
    urlplataforma = models.CharField(max_length=255)
    descripcionplataforma = models.CharField(max_length=200, null=True, blank=True)
    estadoplataforma = models.BooleanField(default=True)
    fechaadquisicionlicencia = models.DateField(null=True, blank=True)
    fechavencimientolicencia = models.DateField(null=True, blank=True)
    contactoplataforma = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombreplataforma


class SesionJuego(models.Model):
    ESTADO_CHOICES = [('Activa', 'Activa'), ('Finalizada', 'Finalizada'), ('Caida', 'Caida')]

    idsesion = models.AutoField(primary_key=True)
    idplataforma = models.ForeignKey(PlataformaJuego, on_delete=models.RESTRICT, db_column='idplataforma', related_name='sesiones')
    idjugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, db_column='idjugador', related_name='sesiones')
    # Nota: el Excel referencia "partidajuego(idpartidajuego)", tabla que no existe en el modelo.
    # Se asume que es un error de tipeo y debe apuntar a PartidaBingo, que sí existe.
    idpartida = models.ForeignKey(PartidaBingo, on_delete=models.CASCADE, db_column='idpartida', related_name='sesiones')
    fechainiciosesion = models.DateTimeField()
    fechafinsesion = models.DateTimeField(null=True, blank=True)
    ipconexion = models.CharField(max_length=50, null=True, blank=True)
    dispositivoconexion = models.CharField(max_length=50, null=True, blank=True)
    estadosesion = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    latenciaping = models.IntegerField(null=True, blank=True)
    navegadorweb = models.CharField(max_length=150, null=True, blank=True)
    tokenconexion = models.CharField(max_length=255, unique=True)
    motivocierre = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Sesión #{self.idsesion} - {self.idjugador}"


# ==========================================
# TABLA DECORATIVA (fuera del modelo E-R)
# ==========================================

class ConfiguracionWeb(models.Model):
    idconfiguracion = models.AutoField(primary_key=True)
    titulosobrenosotros = models.CharField(max_length=150)
    descripcionsobrenosotros = models.TextField()  # Corresponde al varchar(max)
    imagenpromocional = models.CharField(max_length=255)
    numerowhatsapp = models.CharField(max_length=12, validators=[solo_numeros])
    enlaceinstagram = models.CharField(max_length=255, null=True, blank=True)
    enlacefacebook = models.CharField(max_length=255, null=True, blank=True)
    fechaultimaactualizacion = models.DateTimeField()

    def __str__(self):
        return self.titulosobrenosotros