import time

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
from astropy.wcs import WCS
from astroquery.ipac.irsa import Irsa
from firefly_client import FireflyClient


def descargar_recorte_spherex(
    ra, dec, tamano_arcmin=2.0, archivo_salida="spherex_cutout.fits"
):
    """
    Consulta SPHEREx en IRSA, recorta la imagen alrededor de (ra, dec)
    y guarda un nuevo archivo .fits calibrado.
    """
    coord = SkyCoord(ra, dec, unit="deg")
    search_radius = 1 * u.arcsec
    results = None

    # 1. Consultar metadatos en IRSA con reintentos ante errores 502/503
    for intento in range(3):
        try:
            results = Irsa.query_sia(
                pos=(coord, search_radius), collection=["spherex_dr1", "spherex_qr3"]
            )
            break
        except Exception as e:
            espera = 10 * (intento + 1)
            print(f"Servidor ocupado ({e}). Reintentando en {espera}s...")
            time.sleep(espera)

    if results is None or len(results) == 0:
        raise RuntimeError(
            "No se encontraron imágenes de SPHEREx para esas coordenadas."
        )

    # Tomar la URL de la primera exposición encontrada
    access_url = results["access_url"][0]
    print(f"Abriendo exposición remota: {access_url}")

    # 2. Abrir la extensión 'IMAGE' del MEF y extraer sus datos y WCS
    with fits.open(access_url) as hdul:
        ext = "IMAGE" if "IMAGE" in hdul else 1
        data = hdul[ext].data
        header = hdul[ext].header.copy()
        wcs = WCS(header)

    # 3. Realizar el recorte (cutout) centrado en tus coordenadas
    size = u.Quantity((tamano_arcmin, tamano_arcmin), u.arcmin)
    cutout = Cutout2D(data, position=coord, size=size, wcs=wcs, mode="trim")

    # 4. Actualizar la cabecera FITS con las nuevas coordenadas del recorte
    header.update(cutout.wcs.to_header())

    # 5. Guardar el recorte como un archivo .fits independiente en tu disco
    hdu_recorte = fits.PrimaryHDU(data=cutout.data, header=header)
    hdu_recorte.writeto(archivo_salida, overwrite=True)
    print(f"Recorte guardado exitosamente en: {archivo_salida}")

    return archivo_salida


# --- Ejecutar descarga del recorte y visualizar en Firefly (localhost) ---
archivo_fits = descargar_recorte_spherex(
    ra=304.693508808,
    dec=42.4436872991,
    tamano_arcmin=3.0,
    archivo_salida="spherex_cutout.fits",
)

fc = FireflyClient.make_client(url="https://irsa.ipac.caltech.edu/irsaviewer")
fc.launch_browser()
time.sleep(3)

uploaded = fc.upload_file(archivo_fits)
fc.show_fits(uploaded, plot_id="spherex_cutout_view")
