import math

# Distribución chi-cuadrada (valor de tablas)
def _gamma_inc_p(a, x):
    """Función gamma incompleta regularizada P(a, x)."""
    if x <= 0:
        return 0.0
    if x < a + 1:                                   
        ap, s = a, 1.0 / a
        d = s
        for _ in range(2000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    b = x + 1 - a                                   
    c, d = 1e300, 1.0 / b
    h = d
    for i in range(1, 2000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = d if abs(d) > 1e-300 else 1e-300
        c = b + an / c
        c = c if abs(c) > 1e-300 else 1e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return 1 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_cdf(x, gl):
    return _gamma_inc_p(gl / 2.0, x / 2.0)


def chi2_critico(alpha, gl):
    """Valor de tablas χ²(α, gl): x tal que P(X > x) = α."""
    objetivo = 1 - alpha
    lo, hi = 0.0, max(10.0, 5.0 * gl)
    while chi2_cdf(hi, gl) < objetivo:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if chi2_cdf(mid, gl) < objetivo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# Valores críticos de Kolmogorov-Smirnov (α = 0.10, 0.05, 0.01)
_KS_TABLA = {
    1: (0.950, 0.975, 0.995), 2: (0.776, 0.842, 0.929), 3: (0.636, 0.708, 0.828),
    4: (0.565, 0.624, 0.733), 5: (0.509, 0.563, 0.669), 6: (0.468, 0.519, 0.617),
    7: (0.436, 0.483, 0.576), 8: (0.410, 0.454, 0.542), 9: (0.387, 0.430, 0.513),
    10: (0.369, 0.409, 0.489), 11: (0.352, 0.391, 0.468), 12: (0.338, 0.375, 0.449),
    13: (0.325, 0.361, 0.432), 14: (0.314, 0.349, 0.418), 15: (0.304, 0.338, 0.404),
    16: (0.295, 0.327, 0.392), 17: (0.286, 0.318, 0.381), 18: (0.279, 0.309, 0.371),
    19: (0.271, 0.301, 0.361), 20: (0.265, 0.294, 0.352),
}
_KS_ASINTOTICO = {0.10: 1.22, 0.05: 1.36, 0.01: 1.63}  

def ks_critico(n, alpha):
    columna = {0.10: 0, 0.05: 1, 0.01: 2}[round(alpha, 2)]
    if n in _KS_TABLA:
        return _KS_TABLA[n][columna]
    return _KS_ASINTOTICO[round(alpha, 2)] / math.sqrt(n)



# Pruebas
def chi_cuadrada(numeros, alpha=0.05):
    """Prueba Chi-cuadrada de uniformidad con m = √n sub-intervalos."""
    r = [float(x) for x in numeros]
    n = len(r)
    m = max(2, int(math.sqrt(n) + 0.5))
    obs = [0] * m
    for v in r:
        obs[min(int(v * m), m - 1)] += 1           
    esp = n / m
    filas, chi0 = [], 0.0
    for j in range(m):
        parcial = (esp - obs[j]) ** 2 / esp
        chi0 += parcial
        cierre = "]" if j == m - 1 else ")"
        filas.append((f"[{j / m:.4f} , {(j + 1) / m:.4f}{cierre}", obs[j],
                      f"{esp:.4f}", f"{parcial:.4f}"))
    gl = m - 1
    critico = chi2_critico(alpha, gl)
    return {"n": n, "m": m, "E": esp, "gl": gl, "alpha": alpha,
            "columnas": ["Intervalo", "Oi", "Ei = n/m", "(Ei − Oi)² / Ei"],
            "filas": filas, "chi0": chi0, "critico": critico,
            "acepta": chi0 < critico}


def kolmogorov_smirnov(numeros, alpha=0.05):
    """Prueba de Kolmogorov-Smirnov de uniformidad."""
    r = sorted(float(x) for x in numeros)
    n = len(r)
    filas = []
    d_mas = d_menos = 0.0
    for i, ri in enumerate(r, start=1):
        a = i / n - ri
        b = ri - (i - 1) / n
        d_mas, d_menos = max(d_mas, a), max(d_menos, b)
        filas.append((i, f"{i / n:.4f}", f"{ri:.4f}", f"{(i - 1) / n:.4f}",
                      f"{a:.4f}", f"{b:.4f}"))
    d = max(d_mas, d_menos)
    critico = ks_critico(n, alpha)
    return {"n": n, "alpha": alpha,
            "columnas": ["i", "i/n", "ri", "(i−1)/n", "(i/n) − ri", "ri − ((i−1)/n)"],
            "filas": filas, "d_mas": d_mas, "d_menos": d_menos, "d": d,
            "critico": critico, "acepta": d <= critico}