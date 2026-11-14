import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia

def estrellas_gaia(ra, dec, radio_deg):
    centro = SkyCoord(ra, dec, unit="deg")
    job = Gaia.cone_search_async(centro, radius=radio_deg * u.deg)
    return job.get_results().to_pandas()

def marcar_conocidas(cand, gaia_df, tol_arcsec=6.0):
    c = SkyCoord(cand["ra"].values, cand["dec"].values, unit="deg")
    g = SkyCoord(gaia_df["ra"].values, gaia_df["dec"].values, unit="deg")
    _, sep, _ = c.match_to_catalog_sky(g)
    cand = cand.copy()
    cand["en_gaia"] = sep.arcsec < tol_arcsec
    return cand
# convierte cordenadas de el codigo a cordenadas pixeles
def gaia_a_pixeles(gaia_df, wcs):
    coords = SkyCoord(gaia_df["ra"].values, gaia_df["dec"].values, unit="deg")
    x, y = wcs.world_to_pixel(coords)
    return list(zip(x, y))
