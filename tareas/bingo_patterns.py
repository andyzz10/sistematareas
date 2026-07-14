"""
Modalidades de victoria del Bingo.

Cada cartón es una grilla de 5 columnas (B, I, N, G, O) x 5 filas.
Las coordenadas se expresan como (fila, columna) con índices 0-4,
donde columna 0=B, 1=I, 2=N, 3=G, 4=O. La celda (2, 2) es siempre el
espacio FREE (columna N, fila del medio).

Este módulo es la única fuente de verdad para:
1) Dibujar el patrón en "Modalidades de Victoria" (home).
2) Validar si un cartón ganó, comparando contra las balotas cantadas.

NOTA: los patrones de Forma de L, C, T, U, H, Z y Flecha se definieron
a partir de las miniaturas que enviaste. Cuando puedas verlos ya
renderizados, revisa que coincidan celda por celda con lo que esperas
y ajustamos.
"""

COLUMNAS = ['B', 'I', 'N', 'G', 'O']
FILAS = range(5)

CENTRO_FREE = (2, 2)


def _todas():
    return {(f, c) for f in FILAS for c in range(5)}


def _fila(f):
    return {(f, c) for c in range(5)}


def _columna(c):
    return {(f, c) for f in FILAS}


# Patrones de celda fija (conjunto exacto de celdas que deben estar marcadas)
PATRONES_FIJOS = {
    'Tabla Llena': _todas(),
    'Las Cuatro Esquinas': {(0, 0), (0, 4), (4, 0), (4, 4)},
    'En Diagonal': {(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)},
    'Forma de X': {(0, 0), (0, 4), (1, 1), (1, 3), (2, 2), (3, 1), (3, 3), (4, 0), (4, 4)},
    'Forma de Cruz': _fila(2) | _columna(2),
    'Marco de Foto': {(f, c) for f in FILAS for c in range(5) if f in (0, 4) or c in (0, 4)},
    'Forma de L': _columna(0) | _fila(4),
    'Forma de C': _fila(0) | _fila(4) | _columna(0),
    'Forma de T': _fila(0) | _columna(2),
    'Forma de U': _columna(0) | _columna(4) | _fila(4),
    'Forma de H': _columna(0) | _columna(4) | _fila(2),
    'Forma de Z': _fila(0) | _fila(4) | {(1, 3), (2, 2), (3, 1)},
    'Forma de Flecha': {(0, 2), (1, 1), (1, 2), (1, 3), (2, 2), (3, 2), (4, 2)},
}

# Patrones "dinámicos": no es un conjunto fijo, se gana con CUALQUIER fila/columna completa
PATRONES_DINAMICOS = {'Línea Horizontal', 'Línea Vertical'}

# Lista completa en el orden que se muestra en "Academia CoopBingo"
MODALIDADES = [
    'Tabla Llena', 'Las Cuatro Esquinas', 'En Diagonal', 'Forma de X', 'Forma de Cruz',
    'Marco de Foto', 'Línea Horizontal', 'Línea Vertical', 'Forma de L', 'Forma de C',
    'Forma de T', 'Forma de U', 'Forma de H', 'Forma de Z', 'Forma de Flecha',
]

MODALIDAD_CHOICES = [(m, m) for m in MODALIDADES]


def celdas_preview(modalidad):
    """Devuelve el set de celdas a pintar para mostrar el patrón en pantalla.
    Para las dinámicas se ilustra con la fila/columna del medio."""
    if modalidad in PATRONES_FIJOS:
        return PATRONES_FIJOS[modalidad]
    if modalidad == 'Línea Horizontal':
        return _fila(2)
    if modalidad == 'Línea Vertical':
        return _columna(2)
    return set()


def construir_grid_marcado(bolas_cantadas, matriznumeros):
    """Construye una grilla 5x5 de booleanos a partir de las balotas ya
    cantadas y la matriz de números del cartón (dict con B, I, N, G, O)."""
    marcadas = set(bolas_cantadas)
    grid = [[False] * 5 for _ in range(5)]
    for col_idx, letra in enumerate(COLUMNAS):
        for fila_idx, valor in enumerate(matriznumeros[letra]):
            if valor == 'FREE':
                grid[fila_idx][col_idx] = True
            elif valor in marcadas:
                grid[fila_idx][col_idx] = True
    return grid


def verificar_ganador(bolas_cantadas, matriznumeros, modalidad):
    """True si el cartón cumple el patrón de la modalidad con las balotas
    cantadas hasta el momento."""
    grid = construir_grid_marcado(bolas_cantadas, matriznumeros)

    if modalidad == 'Línea Horizontal':
        return any(all(grid[f][c] for c in range(5)) for f in FILAS)
    if modalidad == 'Línea Vertical':
        return any(all(grid[f][c] for f in FILAS) for c in range(5))

    celdas = PATRONES_FIJOS.get(modalidad)
    if not celdas:
        return False
    return all(grid[f][c] for f, c in celdas)