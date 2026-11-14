from fake_data import cubo_sintetico
from detect import normalizar, imagen_diferencia, encontrar_candidatos

def test_detecta_objeto_movil():
    cubo, _ = cubo_sintetico()
    cand = encontrar_candidatos(imagen_diferencia(normalizar(cubo)))
    assert cand["cuadro"].nunique() == len(cubo)
