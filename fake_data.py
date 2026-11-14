import numpy as np

def cubo_sintetico(n=10, tam=128, seed=0):
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 1, (tam, tam))
    estrellas = rng.integers(10, tam - 10, size=(15, 2))
    cubo = []
    
    for i in range(n):
        # Ruido por cuadro
        f = base + rng.normal(0, 0.3, (tam, tam))
        
        # Estrellas estaticas
        for y, x in estrellas:
            f[y - 1:y + 2, x - 1:x + 2] += 20
            
        # divuja el objeto en movimiento
        y, x = 20 + 8 * i, 30 + 6 * i 
        f[y - 1:y + 2, x - 1:x + 2] += 12
        
        cubo.append(f)
        
    fechas = [f"2026-01-{i + 1:02d}" for i in range(n)]
    return np.array(cubo), fechas
