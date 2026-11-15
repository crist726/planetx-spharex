import streamlit as st

from animate import construir_gif, generar_cuadros
from detect import encontrar_candidatos, imagen_diferencia, normalizar
from fake_data import cubo_sintetico

st.set_page_config(page_title="Planet X y SPHEREx", layout="wide")

st.title("Objetos en movimiento con imágenes SPHEREx")

with st.sidebar:
    ra = st.number_input("RA (grados)", value=210.80227, format="%.5f")
    dec = st.number_input("Dec (grados)", value=54.34895, format="%.5f")
    tam = st.slider("Tamaño de la región (grados)", 0.02, 0.5, 0.1)
    banda = st.selectbox(
        "Banda del detector", ["D1", "D2", "D3", "D4", "D5", "D6"], index=1
    )
    intervalo = st.slider("Intervalo del blink (ms)", 100, 1000, 500, step=50)
    escala = st.slider("Zoom", 1, 12, 4)
    vmin, vmax = st.slider("Rango de brillo (min - max)", -10.0, 50.0, (-2.0, 10.0))
    invertir = st.checkbox("Invertir valores de píxeles", value=True)
    modo = st.radio("Modo", ["Normal", "Diferencia"])
    reales = st.checkbox("Usar datos reales de IRSA", value=False)
    gaia = st.checkbox(
        "Superponer estrellas de Gaia DR3 (solo datos reales)", value=False
    )


@st.cache_data(show_spinner="Descargando y alineando imágenes...")
def cargar(ra, dec, tam, banda, reales):
    if reales:
        from data import buscar_observaciones, descargar
        from process import preparar_cuadros

        obs = buscar_observaciones(ra, dec, tam / 2, banda)
        rutas = descargar(obs, "cache", ra, dec, tam)
        return preparar_cuadros(rutas, ra, dec, tam)
    return cubo_sintetico()


cubo, fechas = cargar(ra, dec, tam, banda, reales)
cubo = normalizar(cubo)
dif = imagen_diferencia(cubo)

marcas = None
if gaia and reales:
    from catalogs import estrellas_gaia, gaia_a_pixeles
    from process import wcs_comun

    marcas = gaia_a_pixeles(
        estrellas_gaia(ra, dec, tam / 2), wcs_comun(ra, dec, cubo.shape[1])
    )

vista = dif if modo == "Diferencia" else cubo
cuadros = generar_cuadros(vista, vmin, vmax, escala, invertir, marcas)

tab_anim, tab_cuadro = st.tabs(["Animación", "Cuadro a cuadro"])

with tab_anim:
    st.image(construir_gif(cuadros, intervalo))

with tab_cuadro:
    i = st.slider("Cuadro", 0, len(cuadros) - 1, 0)
    st.image(cuadros[i], caption=f"Fecha: {fechas[i]}")

cand = encontrar_candidatos(dif)
st.subheader("Candidatos")
st.dataframe(cand)
st.download_button("Exportar CSV", cand.to_csv(index=False), "candidatos.csv")
