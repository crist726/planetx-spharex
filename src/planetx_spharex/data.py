import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
import astropy.units as u
from astropy.wcs import WCS
from astroquery.ipac.irsa import Irsa
from firefly_client import FireflyClient

# 1. Discover the exact active SPHEREx collection name on IRSA
collections = Irsa.list_collections()
col_list = collections["collection"] if hasattr(collections, "colnames") else collections
spherex_cols = [str(c) for c in col_list if "spherex" in str(c).lower()]
print("Available IRSA SPHEREx collections:", spherex_cols)

if not spherex_cols:
    raise RuntimeError("No SPHEREx collections found on IRSA. Check astroquery/network status.")

spherex_collection = spherex_cols[0]

# 2. Query a target in the SPHEREx North Ecliptic Pole (NEP) Deep Field
# (Replace with your own SkyCoord once you confirm the collection works)
target = SkyCoord(ra=270.0, dec=66.56, unit="deg", frame="icrs")
sia_table = Irsa.query_sia(pos=(target, 1.0 * u.arcmin), collection=spherex_collection)

# Keep only direct FITS image rows (skip DataLink metadata rows if present)
if "access_format" in sia_table.colnames:
    fits_rows = [r for r in sia_table if "fits" in str(r["access_format"]).lower()]
else:
    fits_rows = list(sia_table)

print(f"Found {len(fits_rows)} overlapping SPHEREx FITS exposures in '{spherex_collection}'.")

wavelengths_um = []
fluxes = []
flux_errs = []

# 3. Extract flux and pixel-dependent LVF wavelength across exposures
for row in fits_rows[:30]:
    fits_url = row["access_url"]

    with fits.open(fits_url) as hdul:
        img_hdr = hdul["IMAGE"].header
        img_data = hdul["IMAGE"].data
        var_data = hdul["VARIANCE"].data
        flags = hdul["FLAGS"].data

        wcs_sky = WCS(img_hdr, naxis=2)
        x_pix, y_pix = wcs_sky.world_to_pixel(target)

        ny, nx = img_data.shape
        if not (5 <= x_pix < nx - 5 and 5 <= y_pix < ny - 5):
            continue

        # Resolve LVF wavelength lookup table ('WCS-WAVE') at detector (x, y)
        wcs_wave = WCS(img_hdr, fobj=hdul, key="W")
        wave_meters = float(np.squeeze(wcs_wave.pixel_to_world_values(x_pix, y_pix)))

        cutout_img = Cutout2D(img_data, position=target, size=3, wcs=wcs_sky)
        cutout_var = Cutout2D(var_data, position=target, size=3, wcs=wcs_sky)
        cutout_flg = Cutout2D(flags, position=target, size=3, wcs=wcs_sky)

        if np.any(cutout_flg.data > 0):
            continue

        wavelengths_um.append(wave_meters * 1e6)
        fluxes.append(np.nansum(cutout_img.data))
        flux_errs.append(np.sqrt(np.nansum(cutout_var.data)))

# 4. Plot the extracted spectrum
order = np.argsort(wavelengths_um)
wave_sorted = np.array(wavelengths_um)[order]
flux_sorted = np.array(fluxes)[order]
err_sorted = np.array(flux_errs)[order]

plt.figure(figsize=(9, 4.5))
plt.errorbar(wave_sorted, flux_sorted, yerr=err_sorted, fmt="o-", markersize=4, capsize=2)
plt.xlabel(r"Wavelength ($\mu\mathrm{m}$)")
plt.ylabel("Aperture Surface Brightness (MJy / sr)")
plt.title(f"SPHEREx Extracted LVF Spectrum ({spherex_collection})")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 5. Open the first FITS exposure in Firefly
if fits_rows:
    fc = FireflyClient.make_client(url="https://irsa.ipac.caltech.edu/irsaviewer")
    fc.show_fits(
        url=fits_rows[0]["access_url"],
        plot_id="spherex-lvf-image",
        title="SPHEREx Level 2 Spectral Image",
    )
