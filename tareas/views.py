from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
import random

from .models import PartidaBingo, CartonPartidaBingo, Carton, Jugador, Bingo
from .forms import RegistroJugadorForm

# ==========================================
# RUTAS DE INICIO Y AUTENTICACIÓN
# ==========================================

def home(request):
    # Traemos los próximos bingos (Programados o En Curso) ordenados por fecha
    proximos_bingos = Bingo.objects.filter(
        estadobingo__in=['Programado', 'En Curso']
    ).order_by('fechaprogramadabingo')[:6] # Mostramos un máximo de 6 en el inicio
    
    return render(request, 'home.html', {'bingos': proximos_bingos})

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': RegistroJugadorForm()})
    else:
        form = RegistroJugadorForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Guardamos la cédula en nuestra tabla Jugador (relacionada al modelo E-R)
            Jugador.objects.create(
                usuario_django=user,
                nombresjugador=user.username,
                aliasjugador=user.username,
                cedulaidentidadjugador=form.cleaned_data['cedula']
            )
            login(request, user)
            return redirect('bingo_lobby')
        else:
            return render(request, 'signup.html', {'form': form, 'error': 'Revisa los datos ingresados.'})

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm(),
                'error': 'Usuario o contraseña incorrectos'
            })
        else:
            login(request, user)
            return redirect('bingo_lobby')

def signout(request):
    logout(request)
    return redirect('home')


# ==========================================
# LÓGICA DEL BINGO VIRTUAL (MODELO E-R)
# ==========================================

@login_required
def bingo_lobby(request):
    if request.method == 'POST':
        partida_id = request.POST.get('id_partida', '').strip()
        if partida_id:
            return redirect('bingo', idpartidabingo=partida_id)
    
    partidas_activas = PartidaBingo.objects.exclude(estadopartida='Finalizada')
    return render(request, 'bingo_lobby.html', {'partidas': partidas_activas})

@login_required
def bingo_view(request, idpartidabingo):
    partida = get_object_or_404(PartidaBingo, pk=idpartidabingo)
    jugador = get_object_or_404(Jugador, usuario_django=request.user)
    
    # Buscamos si el jugador ya tiene un cartón en esta partida
    carton_partida = CartonPartidaBingo.objects.filter(idjugador=jugador, idpartida=partida).first()

    # Si el usuario presiona el botón "Generar mi Cartón"
    if request.method == 'POST' and 'generar_carton' in request.POST:
        if not carton_partida:
            matriz = {
                'B': random.sample(range(1, 16), 5),
                'I': random.sample(range(16, 31), 5),
                'N': random.sample(range(31, 46), 4),
                'G': random.sample(range(46, 61), 5),
                'O': random.sample(range(61, 76), 5),
            }
            matriz['N'].insert(2, "FREE")
            
            # 1. Creamos el cartón físico
            nuevo_carton = Carton.objects.create(
                codigocarton=f"C-{partida.idpartidabingo}-{jugador.idjugador}-{random.randint(1000,9999)}",
                matriznumeros=matriz
            )
            # 2. Lo enlazamos al jugador y a la partida
            carton_partida = CartonPartidaBingo.objects.create(
                idjugador=jugador, 
                idpartida=partida, 
                idcarton=nuevo_carton
            )
        return redirect('bingo', idpartidabingo=partida.idpartidabingo)

    # Preparamos las filas para pintar el cartón si es que ya existe
    filas = []
    if carton_partida:
        matriz_data = carton_partida.idcarton.matriznumeros
        for i in range(5):
            filas.append([
                matriz_data['B'][i], matriz_data['I'][i], matriz_data['N'][i],
                matriz_data['G'][i], matriz_data['O'][i]
            ])

    return render(request, 'bingo.html', {
        'partida': partida,
        'carton': carton_partida.idcarton if carton_partida else None,
        'filas': filas,
        'tiene_carton': bool(carton_partida)
    })

@login_required
def api_estado_partida(request, idpartidabingo):
    partida = get_object_or_404(PartidaBingo, pk=idpartidabingo)
    return JsonResponse({'balotas': partida.bolascantadas})

@login_required
def api_sacar_balota(request, idpartidabingo):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No autorizado'}, status=403)
        
    partida = get_object_or_404(PartidaBingo, pk=idpartidabingo)
    
    if partida.estadopartida == 'Finalizada':
        return JsonResponse({'error': 'Partida Finalizada'}, status=400)

    sacadas = partida.bolascantadas
    disponibles = [n for n in range(1, 76) if n not in sacadas]
    
    if disponibles:
        nueva = random.choice(disponibles)
        sacadas.append(nueva)
        partida.bolascantadas = sacadas
        partida.ultimabola = nueva
        partida.estadopartida = 'En Juego'
        partida.save()
        return JsonResponse({'nueva_balota': nueva, 'balotas': partida.bolascantadas})
        
    return JsonResponse({'error': 'No hay más balotas'}, status=400)
from django.views.decorators.csrf import csrf_exempt

@login_required
def api_obtener_mensajes(request, idbingo):
    mensajes = MensajeChat.objects.filter(idbingo=idbingo).order_by('fechahora')
    data = [{'usuario': m.usuario, 'mensaje': m.mensaje} for m in mensajes]
    return JsonResponse({'mensajes': data})

@csrf_exempt # Necesario para la petición AJAX
@login_required
def api_enviar_mensaje(request, idbingo):
    if request.method == 'POST':
        datos = json.loads(request.body)
        bingo = get_object_or_404(Bingo, pk=idbingo)
        MensajeChat.objects.create(
            idbingo=bingo,
            usuario=request.user.username,
            mensaje=datos['mensaje']
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Solo POST'}, status=400) 