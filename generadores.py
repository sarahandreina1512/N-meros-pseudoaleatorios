import math
import random
from dataclasses import dataclass, field


@dataclass
class Resultado:
    clave: str
    nombre: str
    parametros: dict
    columnas: list
    filas: list
    numeros: list
    notas: list = field(default_factory=list)
    interpretacion: str = ""

def centro(valor, d):
    """Devuelve los D dígitos del centro de `valor`.
    Si hace falta, se agregan ceros a la izquierda (hasta 2D dígitos)."""
    s = str(valor).zfill(2 * d)
    ini = (len(s) - d) // 2
    return s[ini:ini + d]


def _semilla(rng, d):
    """Entero aleatorio de exactamente D dígitos."""
    return rng.randint(10 ** (d - 1), 10 ** d - 1)


def _sin_degenerar(numeros):
    """True si no hay ceros ni valores repetidos (ciclos) en la secuencia."""
    return len(set(numeros)) == len(numeros) and all(float(r) != 0 for r in numeros)


# Métodos 
def cuadrados_medios(n, semilla, d):
    """Y_i = X_i^2 ; X_{i+1} = D dígitos del centro ; r_{i+1} = 0.X_{i+1}"""
    filas, numeros = [], []
    x = semilla
    for i in range(n):
        y = x * x
        c = centro(y, d)
        r = f"0.{c}"
        filas.append((i, str(x).zfill(d), str(y).zfill(2 * d), c, r))
        numeros.append(r)
        x = int(c)
    columnas = ["i", "Xi", "Yi = Xi²", "Xi+1 (centro)", "ri+1"]
    return columnas, filas, numeros


def productos_medios(n, semilla0, semilla1, d):
    """Y_i = X_i * X_{i+1} ; X_{i+2} = D dígitos del centro ; r_{i+1} = 0.X_{i+2}"""
    filas, numeros = [], []
    a, b = semilla0, semilla1
    for i in range(n):
        y = a * b
        c = centro(y, d)
        r = f"0.{c}"
        filas.append((i, str(a).zfill(d), str(b).zfill(d), str(y).zfill(2 * d), c, r))
        numeros.append(r)
        a, b = b, int(c)         
    columnas = ["i", "Xi", "Xi+1", "Yi = Xi · Xi+1", "Xi+2 (centro)", "ri+1"]
    return columnas, filas, numeros


def multiplicador_constante(n, semilla, constante, d):
    """Y_i = a * X_i ; X_{i+1} = D dígitos del centro ; r_{i+1} = 0.X_{i+1}"""
    filas, numeros = [], []
    x = semilla
    for i in range(n):
        y = constante * x
        c = centro(y, d)
        r = f"0.{c}"
        filas.append((i, str(x).zfill(d), str(constante), str(y).zfill(2 * d), c, r))
        numeros.append(r)
        x = int(c)
    columnas = ["i", "Xi", "a", "Yi = a · Xi", "Xi+1 (centro)", "ri+1"]
    return columnas, filas, numeros


def lineal(x0, a, c, m):
    """X_{i+1} = (a X_i + c) mod m ; r = X / (m - 1).
    Genera números hasta que se vuelve a obtener la semilla X0 (periodo de vida)."""
    filas, numeros, enteros = [], [], []
    x = x0
    for i in range(m):                      
        t = a * x + c
        sig = t % m
        r = f"{sig / (m - 1):.3f}"
        filas.append((i + 1, x, f"{a}·{x} + {c} = {t}", sig, r))
        numeros.append(r)
        enteros.append(sig)
        x = sig
        if sig == x0:
            break
    columnas = ["i", "Xi-1", "a·Xi-1 + c", "Xi = (a·Xi-1 + c) mod m", "ri = Xi / (m-1)"]
    return columnas, filas, numeros, enteros

# Metodos congruenciales
def congruencial_multiplicativo(x0, a, m):
    """X_{i+1} = (a X_i) mod m ; r = X / (m - 1).
    Genera números hasta que se vuelve a obtener la semilla X0 (periodo de vida)."""
    filas, numeros = [], []
    x = x0
    for i in range(m):
        t = a * x
        sig = t % m
        r = f"{sig / (m - 1):.3f}"
        filas.append((i + 1, x, f"{a}·{x} = {t}", sig, r))
        numeros.append(r)
        x = sig
        if sig == x0:
            break
    columnas = ["i", "Xi-1", "a·Xi-1", "Xi = (a·Xi-1) mod m", "ri = Xi / (m-1)"]
    return columnas, filas, numeros


NOTA_DEGENERA = ("La secuencia presenta ceros o ciclos cortos; es una limitación "
                 "conocida de este método con semillas pequeñas.")


def _gen_cuadrados(n, rng):
    for _ in range(300):
        d = rng.randint(4, 6)
        x0 = _semilla(rng, d)
        cols, filas, nums = cuadrados_medios(n, x0, d)
        if _sin_degenerar(nums):
            return {"D (dígitos)": d, "Semilla X0": x0}, cols, filas, nums, []
    return {"D (dígitos)": d, "Semilla X0": x0}, cols, filas, nums, [NOTA_DEGENERA]


def _gen_productos(n, rng):
    for _ in range(300):
        d = rng.randint(4, 6)
        x0, x1 = _semilla(rng, d), _semilla(rng, d)
        cols, filas, nums = productos_medios(n, x0, x1, d)
        if _sin_degenerar(nums):
            return {"D (dígitos)": d, "Semilla X0": x0, "Semilla X1": x1}, cols, filas, nums, []
    return {"D (dígitos)": d, "Semilla X0": x0, "Semilla X1": x1}, cols, filas, nums, [NOTA_DEGENERA]


def _gen_multiplicador(n, rng):
    for _ in range(300):
        d = rng.randint(4, 6)
        x0, a = _semilla(rng, d), _semilla(rng, d)
        cols, filas, nums = multiplicador_constante(n, x0, a, d)
        if _sin_degenerar(nums):
            return {"D (dígitos)": d, "Semilla X0": x0, "Constante a": a}, cols, filas, nums, []
    return {"D (dígitos)": d, "Semilla X0": x0, "Constante a": a}, cols, filas, nums, [NOTA_DEGENERA]


def _gen_lineal(n, rng):
    # Banks, Carson, Nelson y Nicol: m = 2^g, a = 1 + 4k, c relativamente primo a m,
    # k y g enteros  ->  periodo de vida máximo N = m = 2^g
    g = rng.randint(3, 8)
    m = 2 ** g
    k = rng.randint(1, 20)
    a = 1 + 4 * k
    c = rng.choice([v for v in range(1, m) if math.gcd(v, m) == 1])
    x0 = rng.randint(1, m - 1)

    cols, filas, nums, enteros = lineal(x0, a, c, m)
    N = len(filas)
    distintos = sorted(set(enteros))
    if len(distintos) <= 16:
        secuencia = ", ".join(str(v) for v in distintos)
    else:                                 
        secuencia = f"0, 1, 2, 3, ..., {distintos[-1]}"
    completa = len(distintos) == m
    interpretacion = (
        f"Se cumplen las condiciones de Banks, Carson, Nelson y Nicol (m = 2^g, a = 1 + 4k, "
        f"c relativamente primo a m, g y k enteros), por lo que se logra el periodo de vida "
        f"máximo N = m = 2^{g} = {m}.\n"
        f"El número generado en X{N} = {x0} es exactamente igual a la semilla X0, y si "
        f"continuáramos generando más números, éstos se repetirían.\n"
        f"Además, el algoritmo genera una secuencia de números enteros "
        f"S = {{0, 1, 2, 3, ..., m-1}}; en este caso se genera S = {{{secuencia}}} "
        f"({'todos los valores posibles' if completa else str(len(distintos)) + ' valores'})."
    )
    params = {"g": g, "m = 2^g": m, "k": k, "a = 1 + 4k": a,
              "c (primo relativo a m)": c, "Semilla X0": x0}
    return params, cols, filas, nums, [], interpretacion


def _gen_multiplicativo(n, rng):
    # m = 2^g, a = 3 + 8k ó 5 + 8k, X0 impar, g entero -> periodo máximo N = m/4 = 2^(g-2)
    g = rng.randint(4, 9)
    m = 2 ** g
    base = rng.choice([3, 5])
    k = rng.randint(0, 20)
    a = base + 8 * k
    x0 = rng.randrange(1, m, 2)

    cols, filas, nums = congruencial_multiplicativo(x0, a, m)
    N = len(filas)
    interpretacion = (
        f"Si la semilla X0 = {x0} se repite, volverán a generarse los mismos números. "
        f"Por lo tanto, el periodo de vida es n = {N}, el cual corresponde a "
        f"N = m/4 = 2^{g}/4 = 2^({g}-2) = {m // 4}."
    )
    params = {"g": g, "m = 2^g": m, f"a = {base} + 8k": a, "k": k,
              "Semilla X0 (impar)": x0}
    return params, cols, filas, nums, [], interpretacion


METODOS = {
    "cuadrados": {
        "nombre": "Algoritmo de Cuadrados Medios",
        "pestana": "Cuadrados medios",
        "descripcion": ("Se eleva al cuadrado una semilla de D dígitos y se toman los D dígitos "
                        "del centro; el número r se forma anteponiendo «0.». Luego se repite el "
                        "procedimiento con esos D dígitos (si hace falta, se agregan ceros a la izquierda)."),
        "funcion": _gen_cuadrados,
    },
    "productos": {
        "nombre": "Algoritmo de Productos Medios",
        "pestana": "Productos medios",
        "descripcion": ("Requiere dos semillas de D dígitos. Se multiplican y del producto se toman los "
                        "D dígitos del centro para formar r. Se elimina la semilla más antigua y se "
                        "multiplica la otra por el nuevo número, y así sucesivamente."),
        "funcion": _gen_productos,
    },
    "multiplicador": {
        "nombre": "Algoritmo de Multiplicador Constante",
        "pestana": "Multiplicador constante",
        "descripcion": ("Similar al de productos medios, pero una constante a de D dígitos multiplica "
                        "siempre a la semilla actual; del producto se toman los D dígitos del centro."),
        "funcion": _gen_multiplicador,
    },
    "lineal": {
        "nombre": "Algoritmo Congruencial Lineal",
        "pestana": "Lineal",
        "descripcion": ("Propuesto por D. H. Lehmer (1951). Genera enteros con la recursión "
                        "Xi+1 = (a·Xi + c) mod m y los convierte al intervalo (0, 1) con "
                        "ri = Xi / (m − 1). Se generan números hasta encontrar el periodo de vida "
                        "máximo N = m = 2^g (cuando la semilla X0 se repite)."),
        "funcion": _gen_lineal,
    },
    "multiplicativo": {
        "nombre": "Algoritmo Congruencial Multiplicativo",
        "pestana": "Multiplicativo",
        "descripcion": ("Surge del lineal cuando c = 0: Xi+1 = (a·Xi) mod m, con ri = Xi / (m − 1). "
                        "Para lograr el periodo máximo: m = 2^g, a = 3 + 8k ó 5 + 8k, X0 impar. "
                        "Se generan números hasta que la semilla X0 se repite."),
        "funcion": _gen_multiplicativo,
    },
}


def generar(clave, n, rng=None):
    """Elige parámetros aleatorios para el método `clave` y genera los números."""
    rng = rng or random.SystemRandom()
    info = METODOS[clave]
    salida = info["funcion"](n, rng)
    params, cols, filas, nums, notas = salida[:5]
    interpretacion = salida[5] if len(salida) > 5 else ""
    return Resultado(clave, info["nombre"], params, cols, filas, nums, notas, interpretacion)