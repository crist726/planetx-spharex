import numpy as np
import pandas as pd
from scipy import ndimage
def normalizar(cubo):
out = []
for f in cubo:
fondo = np.nanmedian(f)
ruido = 1.4826 * np.nanmedian(np.abs(f - fondo))
out.append((f - fondo) / ruido)
return np.array(out)
def imagen_diferencia(cubo):
return cubo - np.nanmedian(cubo, axis=0)
def encontrar_candidatos(cubo_dif, umbral=5):
filas = []
for i, f in enumerate(cubo_dif):
etiquetas, n = ndimage.label(np.nan_to_num(f) > umbral)
if n == 0:
continue
for y, x in ndimage.center_of_mass(np.nan_to_num(f), etiquetas,
range(1, n + 1)):
filas.append({"cuadro": i, "x": x, "y": y})
return pd.DataFrame(filas, columns=["cuadro", "x", "y"])
