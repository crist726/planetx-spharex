import io
import numpy as np
from PIL import Image, ImageDraw
#convertir cubo de datos numeros a animados , como un gif, este no usa datos sinteticos no quitarxd
def generar_cuadros(cubo, vmin=-2, vmax=10, escala=4, invertir=False, marcas=None):
    """marcas: lista de (x, y) en píxeles del cubo; se dibujan como círculos rojos."""
    out = []
    for f in cubo:
        n = np.nan_to_num(np.clip((f - vmin) / (vmax - vmin), 0, 1))
        if invertir:
            n = 1 - n
        im = Image.fromarray((n * 255).astype(np.uint8)).convert("RGB")
        im = im.resize((im.width * escala, im.height * escala), Image.NEAREST)
        if marcas:
            d = ImageDraw.Draw(im)
            r = 3 * escala
            for x, y in marcas:
                cx, cy = (x + 0.5) * escala, (y + 0.5) * escala
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 0, 0), width=2)
        out.append(im)
    return out

def construir_gif(cuadros, intervalo_ms=500):
    buf = io.BytesIO()
    cuadros[0].save(
        buf, 
        format="GIF", 
        save_all=True, 
        append_images=cuadros[1:], 
        duration=intervalo_ms, 
        loop=0
    )
    return buf.getvalue()
