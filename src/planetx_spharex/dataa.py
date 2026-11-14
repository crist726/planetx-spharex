from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.ipac.irsa import Irsa


def descargar_fits(ra, dec):
    """
    Descargar información de imagenes de SHAPEx

    Args:
        ra: Ascensión Recta en grados nomales (equivalente a longitud geográfrica)
        dec: Declinación en grados normales (equivalnete a latitud)
    """

    coord = SkyCoord(ra, dec, unit="deg")
    search_radius = 1 * u.arcsec

    # Regresa (no funciona siempre 502 error) los datos de IRS
    # nos falta retrivir las imagenes(s)
    results = Irsa.query_sia(
        pos=(coord, search_radius), collection=["spherex_dr1", "spherex_qr3"]
    )

    # Se supone que es la imagen tal cual
    spectral_image_url = results["access_url"][0]
    return spectral_image_url


ra_deg = 20
dec_deg = 30
print(descargar_fits(ra_deg, dec_deg))
