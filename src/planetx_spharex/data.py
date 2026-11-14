import time

import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D, NoOverlapError
from astropy.utils.data import download_file
from astropy.visualization import simple_norm
from astropy.wcs import WCS
from astroquery.ipac.irsa import Irsa


def descargar_fits(ra, dec, guardar_fits=True):
    """
    Descarga una imagen FITS de SPHEREx desde IRSA y genera un recorte en PNG.

    Args:
        ra (float): Ascensión Recta en grados decimales.
        dec (float): Declinación en grados decimales.
        guardar_fits (bool): Si es True, guarda el archivo .fits en disco.
    """
    coord = SkyCoord(ra, dec, unit="deg")
    search_radius = 1 * u.arcsec
    results = None

    # 1. Consulta SIA con reintentos ante errores 502 / timeouts
    for intento in range(3):
        try:
            results = Irsa.query_sia(
                pos=(coord, search_radius),
                collection=["spherex_dr1", "spherex_qr3"],
            )
            break
        except Exception as e:
            espera = 10 * (intento + 1)
            print(
                f"Intento {intento + 1}/3 fallido en query_sia ({e}). Reintentando en {espera}s..."
            )
            time.sleep(espera)

    if results is None:
        raise RuntimeError("No se pudo conectar con IRSA tras 3 intentos.")

    if len(results) == 0:
        print(f"No se encontraron observaciones de SPHEREx en RA={ra}, Dec={dec}.")
        return None

    # Filtrar solo enlaces que apunten a archivos FITS
    if "access_format" in results.colnames:
        mask_fits = ["fits" in str(fmt).lower() for fmt in results["access_format"]]
        if any(mask_fits):
            results = results[mask_fits]

    fits_url = results["access_url"][0]

    # 2. Descarga del FITS con reintentos
    ruta_local = None
    for intento in range(3):
        try:
            ruta_local = download_file(fits_url, cache=True, timeout=60)
            break
        except Exception as e:
            espera = 10 * (intento + 1)
            print(
                f"Intento {intento + 1}/3 fallido al descargar FITS ({e}). Reintentando en {espera}s..."
            )
            time.sleep(espera)

    if ruta_local is None:
        raise RuntimeError(f"No se pudo descargar el archivo FITS desde {fits_url}.")

    # 3. Lectura de datos y WCS
    with fits.open(ruta_local) as hdul:
        if guardar_fits:
            hdul.writeto("spherex_imagen.fits", overwrite=True)

        ext = "IMAGE" if "IMAGE" in hdul else 1
        data = hdul[ext].data
        wcs = WCS(hdul[ext].header, naxis=2)

    # 4. Recorte 2D y guardado de PNG
    try:
        cutout = Cutout2D(
            data,
            position=coord,
            size=(3 * u.arcmin, 3 * u.arcmin),
            wcs=wcs,
            mode="trim",
        )
    except NoOverlapError:
        print("La coordenada no se superpone con el área válida de la imagen.")
        return None

    if cutout.data.size == 0 or np.all(np.isnan(cutout.data)):
        print("El recorte está vacío o contiene únicamente valores NaN.")
        return None

    norm = simple_norm(cutout.data, "asinh", percent=99.5)
    datos_normalizados = norm(cutout.data)
    plt.imsave(
        "spherex_imagen.png",
        datos_normalizados,
        cmap="inferno",
        vmin=0,
        vmax=1,
        origin="lower",
    )
    print(f"Listo. Se encontraron {len(results)} imágenes; se procesó la primera.")
    return results


ra_deg = 310
dec_deg = 80

descargar_fits(ra_deg, dec_deg)
