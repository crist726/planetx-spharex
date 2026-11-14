import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_interp
def wcs_comun(ra, dec, tam_pix, escala_arcsec=6.15):
w = WCS(naxis=2)
w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
w.wcs.crval = [ra, dec]
w.wcs.crpix = [tam_pix / 2, tam_pix / 2]
w.wcs.cdelt = [-escala_arcsec / 3600, escala_arcsec / 3600]
return w
def preparar_cuadros(rutas, ra, dec, tam_deg, escala_arcsec=6.15):
Plan del equipo: herramienta pública con imágenes SPHEREx (Planet X)
Page 14 of 25
tam_pix = int(tam_deg * 3600 / escala_arcsec)
destino = wcs_comun(ra, dec, tam_pix, escala_arcsec)
cubo, fechas = [], []
for ruta in rutas:
with fits.open(ruta) as hdul: # confirmar nombres con
hdul.info()
img = hdul["IMAGE"].data.astype(float)
wcs = WCS(hdul["IMAGE"].header)
img[hdul["FLAGS"].data != 0] = np.nan # afinar qué bits excluir
alineada, _ = reproject_interp((img, wcs), destino, shape_out=
(tam_pix, tam_pix))
cubo.append(alineada)
fechas.append(hdul["IMAGE"].header.get("DATE-OBS", ruta))
return np.array(cubo), fechas
