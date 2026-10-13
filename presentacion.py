"""
Presentación de la charla, hecha con Streamlit.

Cada slide es una función. En los slides de código, el código que se ve
es exactamente el que se ejecuta: el resultado aparece al lado, en vivo.

Navegar: botones al pie, o las flechas ← → del teclado.
"""

from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from PIL import Image, ImageOps

from datos import cargar_datos

CARPETA = Path(__file__).parent
NOMBRE = "Maria Clara Sanchez"
ROL = "Ingeniera de Software"
FECHA = "22 de octubre de 2026"
FOTO = CARPETA / "assets" / "me.JPEG"
FOTOS_PERSONALES = [
    (CARPETA / "assets" / "g1.JPEG", 0.08),
    (CARPETA / "assets" / "g3.JPEG", 0.45),
    (CARPETA / "assets" / "g2.JPEG", 0.45),
]
BIO = [
    "Ingeniera de Computación, **+4 años** en desarrollo de software",
    "Ingeniera de Software Backend en **CI&T** (sector financiero)",
    "Python, backend y APIs REST: mi día a día",
    "Maestría en Ciencias de la Computación · **ICMC-USP**",
    "Foco en Sistemas Distribuidos y Programación Concurrente",
]
REPO_URL = ""
CONTACTO = {
    "Correo": "",
    "LinkedIn": "",
    "GitHub": "",
}

COMPUERTAS = [
    (
        "Layout con columnas y métricas",
        "st.columns + st.metric",
        ":material/view_column:",
    ),
    ("Gráficos que destacan", "st.bar_chart", ":material/bar_chart:"),
    ("Sidebar y tabs", "organización profesional", ":material/tab:"),
    ("Interactividad completa", "selectbox, progress y más", ":material/touch_app:"),
    (
        "Estado entre interacciones",
        "st.session_state y st.cache_data",
        ":material/memory:",
    ),
    ("Tema visual", "colores propios, sin CSS", ":material/palette:"),
]

# Cuenta cuántas veces se ejecutó este script (lo usamos en la 5ª compuerta).
st.session_state.ejecuciones = st.session_state.get("ejecuciones", 0) + 1


# ---------------------------------------------------------------------------
# Piezas reutilizables de los slides
# ---------------------------------------------------------------------------
SLIDES = []


def slide(titulo: str, pasos: int = 1):
    """Registra una función como slide, en el orden en que se define.

    `pasos` > 1 revela el contenido por partes: la flecha → muestra el
    siguiente paso antes de pasar al próximo slide.
    """

    def registrar(funcion):
        SLIDES.append({"titulo": titulo, "pasos": pasos, "funcion": funcion})
        return funcion

    return registrar


def aparece(paso: int) -> bool:
    """True a partir del paso indicado del slide actual (el primero es 0)."""
    return st.session_state.paso >= paso


def encabezado(
    etiqueta: str | None, titulo: str, subtitulo: str | None = None, icono=None
):
    """Etiqueta + título + subtítulo: el mismo formato en todos los slides."""
    if etiqueta:
        st.badge(etiqueta.upper(), icon=icono, color="blue")
    st.title(titulo)
    if subtitulo:
        st.markdown(f"#### :gray[{subtitulo}]")
    st.space("small")


def marcador_compuerta(actual: int):
    """Fila con las 6 compuertas: hechas, actual y pendientes."""
    with st.container(horizontal=True, gap="small"):
        for numero, (nombre, _, icono) in enumerate(COMPUERTAS, start=1):
            if numero < actual:
                st.badge(str(numero), icon=":material/check:", color="blue")
            elif numero == actual:
                st.badge(f"{numero} · {nombre}", icon=icono, color="yellow")
            else:
                st.badge(str(numero), color="gray")


@st.cache_data
def recorte_cuadrado(archivo: Path, altura_rostro: float = 0.27) -> Image.Image:
    """Recorta una foto vertical en cuadrado, sin tocar el archivo original.

    `altura_rostro` elige qué parte se conserva: 0 = arriba, 1 = abajo.
    """
    foto = ImageOps.exif_transpose(Image.open(archivo))
    lado = min(foto.size)
    x = (foto.width - lado) // 2
    y = int((foto.height - lado) * altura_rostro)
    return foto.crop((x, y, x + lado, y + lado))


def foto_o_marcador(
    archivo: Path,
    alt: str,
    altura: int,
    pie: str | None = None,
    cuadrada: bool = False,
    encuadre: float = 0.27,
    ancho: int | str = "stretch",
):
    """Muestra la foto si existe; si no, un recuadro que indica dónde ponerla."""
    if archivo.exists():
        imagen = recorte_cuadrado(archivo, encuadre) if cuadrada else archivo
        st.image(imagen, caption=pie, width=ancho, alt=alt)
        return
    with st.container(
        border=True,
        width=ancho,
        height=altura,
        horizontal_alignment="center",
        vertical_alignment="center",
    ):
        st.markdown("### :material/add_a_photo:")
        st.caption(f"Tu foto aquí: `assets/{archivo.name}`")


def tarjeta(titulo: str, texto: str, icono: str = ""):
    with st.container(border=True, height="stretch"):
        st.markdown(f"### {icono} {titulo}".strip())
        st.markdown(f":gray[{texto}]")


def datos_de_la_charla() -> list[dict]:
    """Los 10 datasets más descargados, en el formato crudo de la API."""
    return cargar_datos()["crudo"].head(10).tolist()


class StConBarraSimulada:
    """Igual a `st`, pero `st.sidebar` apunta a un recuadro dentro del slide.

    Así el código del slide usa `with st.sidebar:` de verdad, sin mezclar
    sus filtros con los controles de la presentación en la barra real.
    """

    def __init__(self, barra):
        self.sidebar = barra

    def __getattr__(self, nombre):
        return getattr(st, nombre)


def codigo_en_vivo(
    codigo: str, proporcion=(1, 1), barra_simulada: bool = False, apilado: bool = False
):
    """Muestra el código a la izquierda y lo ejecuta a la derecha.

    Con `apilado=True` el resultado va debajo del código y usa todo el ancho.
    """
    if apilado:
        izquierda, derecha = st.container(), st.container()
    else:
        izquierda, derecha = st.columns(proporcion, gap="large")
    with izquierda:
        st.markdown(":blue[:material/code:] **El código**")
        st.code(codigo)
    with derecha, st.container(border=True):
        st.markdown(":orange[:material/play_circle:] **El resultado, en vivo**")
        modulo_st = st
        if barra_simulada:
            # La barra simulada va arriba, en una franja: así el contenido usa todo el ancho
            st.caption(":material/left_panel_open: Barra lateral")
            barra = st.container(
                border=True, horizontal=True, vertical_alignment="center"
            )
            modulo_st = StConBarraSimulada(barra)
        columna_contenido = st.container()
        with columna_contenido:
            try:
                exec(
                    codigo,
                    {
                        "st": modulo_st,
                        "requests": requests,
                        "datos": datos_de_la_charla(),
                    },
                )
            except requests.RequestException as error:
                st.error(f"No se pudo consultar la API ahora: {error}")


# ---------------------------------------------------------------------------
# Apertura
# ---------------------------------------------------------------------------
@slide("Portada")
def portada():
    st.space("large")
    texto, vivo = st.columns([3, 2], gap="large", vertical_alignment="center")
    with texto:
        with st.container(horizontal=True):
            st.badge("PyCon Panamá", icon=":material/mic:", color="yellow")
            st.badge("Hecho 100% con Streamlit", icon=":material/bolt:", color="blue")
        st.title("Monitoreando los :yellow-background[datos] que entrenan la IA")
        st.markdown(
            "#### :gray[Un panel profesional con Streamlit: layout, interactividad, "
            "estado y tema visual, en vivo y solo con Python.]"
        )
        st.space("small")
        linea = f"**{NOMBRE}** · {ROL}"
        if FECHA:
            linea += f" · {FECHA}"
        st.markdown(linea)
    with vivo, st.container(border=True):
        st.badge(
            "En vivo desde Hugging Face Hub", icon=":material/sensors:", color="green"
        )
        try:
            datos = cargar_datos()
            lider = datos.iloc[0]
            st.metric("Dataset más descargado del mes", lider["nombre"])
            st.metric(
                "Descargas en los últimos 30 días",
                f"{lider['descargas'] / 1e6:,.1f} M",
                chart_data=datos["descargas"].head(30).tolist(),
                chart_type="bar",
            )
        except requests.RequestException:
            st.caption("Sin conexión con la API en este momento.")
    st.space("medium")


@slide("Quién les habla", pasos=2)
def quien():
    encabezado("Quién les habla hoy", NOMBRE, ROL, ":material/person:")
    foto, texto = st.columns([2, 5], gap="large")
    with foto:
        foto_o_marcador(FOTO, alt=f"Foto de {NOMBRE}", altura=260, cuadrada=True)
    with texto:
        for item in BIO:
            st.markdown(f":blue[:material/arrow_right:] {item}")
        if aparece(1):
            with st.container(key="paso-1"):
                st.space("small")
                st.markdown(":material/pets: **Fuera del código**")
                with st.container(horizontal=True, gap="medium"):
                    for archivo, encuadre in FOTOS_PERSONALES:
                        foto_o_marcador(
                            archivo,
                            alt="Mis mascotas",
                            altura=250,
                            cuadrada=True,
                            encuadre=encuadre,
                            ancho=250,
                        )


@slide("El problema", pasos=2)
def problema():
    encabezado(
        "El problema",
        "Un buen dashboard todavía cuesta caro",
        icono=":material/report:",
    )
    antes, hoy = st.columns(2, gap="large")
    with antes, st.container(border=True):
        st.subheader(":material/hourglass_top: Camino tradicional")
        for item in [
            "Back-end para servir los datos",
            "Front-end en HTML, CSS y JavaScript",
            "Framework de UI (React, Vue…)",
            "Desplegar dos sistemas",
        ]:
            st.markdown(f":gray[:material/remove:] {item}")
        st.metric("Resultado", "días o semanas")
    if aparece(1):
        with hoy, st.container(border=True, key="paso-1"):
            st.subheader(":blue[:material/rocket_launch:] Lo que haremos hoy")
            for item in [
                "Tomar datos reales ya listos",
                "Un panel con layout profesional",
                "Interactividad y estado",
                "Un tema visual propio",
            ]:
                st.markdown(f":blue[:material/check:] {item}")
            st.metric("Resultado", "30 minutos")


@slide("Qué es Streamlit", pasos=2)
def que_es():
    st.space("large")
    st.badge("STREAMLIT EN UNA FRASE", icon=":material/bolt:", color="blue")
    st.title(
        "“Streamlit transforma un script de Python en una :yellow-background[app web]: "
        "una función por cada elemento de la interfaz.”"
    )
    if aparece(1):
        with st.container(key="paso-1"):
            st.space("medium")
            st.markdown(
                "### `st.title()` :gray[→] `st.columns()` :gray[→] `st.tabs()` "
                ":gray[→] :blue[**listo.**]"
            )


@slide("Hola, Streamlit")
def hola_streamlit():
    encabezado(
        "Primer contacto",
        "Unas líneas de Python, una :yellow-background[app web]",
        "Cada función de `st` dibuja un elemento en la pantalla.",
        ":material/waving_hand:",
    )
    codigo_en_vivo(
        """\
import streamlit as st

st.title("¡Hola, PyCon Panamá! 👋")
nombre = st.text_input("¿Cómo te llamas?")
if nombre:
    st.success(f"Bienvenida/o, {nombre}")
"""
    )
    st.caption("Para correrlo: `pip install streamlit` y luego `streamlit run app.py`.")


@slide("Dónde brilla", pasos=2)
def donde_brilla():
    encabezado(
        "Eligiendo la herramienta correcta",
        "Dónde brilla Streamlit (y dónde no)",
        icono=":material/balance:",
    )
    si, no = st.columns(2, gap="large")
    with si, st.container(border=True, height="stretch"):
        st.subheader(":blue[:material/thumb_up:] Ideal para")
        for item in [
            "Dashboards internos",
            "Prototipos de ML y ciencia de datos",
            "Herramientas rápidas para el equipo",
            "Pruebas de concepto",
        ]:
            st.markdown(f":blue[:material/check:] {item}")
    if aparece(1):
        with no, st.container(border=True, height="stretch", key="paso-1"):
            st.subheader(":orange[:material/warning:] No es ideal para")
            for item in [
                "Interfaces 100% personalizadas",
                "Millones de usuarios simultáneos",
                "Flujos complejos de permisos",
            ]:
                st.markdown(f":orange[:material/close:] {item}")


# ---------------------------------------------------------------------------
# Los datos: la API pública de Hugging Face Hub
# ---------------------------------------------------------------------------
@slide("De dónde vienen los datos", pasos=2)
def hugging_face():
    encabezado(
        "Los datos",
        "Hugging Face Hub: el :yellow-background[GitHub de la IA]",
        "Donde empresas, universidades y la comunidad publican lo que usan para crear IA.",
        ":material/hub:",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        tarjeta(
            "Modelos",
            "Redes ya entrenadas: Llama, Whisper, BERT…",
            ":material/neurology:",
        )
    with c2:
        tarjeta(
            "Datasets",
            "Datos para entrenar y evaluar modelos: FineWeb, Common Voice, SQuAD… "
            "**Es lo que vamos a monitorear.**",
            ":material/dataset:",
        )
    with c3:
        tarjeta(
            "Spaces",
            "Apps de demostración, muchas hechas con Streamlit.",
            ":material/apps:",
        )
    if aparece(1):
        with st.container(key="paso-1"):
            st.space("small")
            st.info(
                "**La API devuelve la *ficha* de cada dataset, no los datos en sí**, como la ficha "
                "de un libro en la biblioteca. Pública, en JSON, sin clave ni registro.",
                icon=":material/lightbulb:",
            )


@slide("Es solo una URL")
def solo_una_url():
    encabezado(
        "La API pública",
        "Es solo una URL que devuelve JSON",
        "Cambia los parámetros: la URL y los resultados se actualizan en vivo.",
        ":material/link:",
    )
    codigo_en_vivo(
        """\
orden = st.segmented_control(
    "Ordenar por",
    ["downloads", "likes", "trendingScore"],
    default="downloads",
    required=True,
)
limite = st.slider("Cuántos datasets", 3, 10, 5)

url = "https://huggingface.co/api/datasets"
params = {"sort": orden, "direction": -1, "limit": limite}
respuesta = requests.get(url, params=params, timeout=10)

st.code(respuesta.url, language=None, wrap_lines=True)
st.dataframe(respuesta.json(),
             column_order=["id", "downloads", "likes"])
""",
    )


# ---------------------------------------------------------------------------
# Las 6 compuertas
# ---------------------------------------------------------------------------
@slide("El recorrido")
def recorrido():
    encabezado(
        "El recorrido",
        "Seis compuertas hasta un panel :yellow-background[bonito]",
        "Todo en Python puro. El foco de hoy: Streamlit a fondo.",
        ":material/route:",
    )
    for fila in (COMPUERTAS[:3], COMPUERTAS[3:]):
        columnas = st.columns(3)
        for columna, compuerta in zip(columnas, fila):
            nombre, detalle, icono = compuerta
            numero = COMPUERTAS.index(compuerta) + 1
            with columna, st.container(border=True, height="stretch"):
                st.markdown(f"### :blue[{icono}] {numero}")
                st.markdown(f"**{nombre}**")
                st.caption(detalle)


@slide("1ª compuerta — Layout")
def compuerta_1():
    marcador_compuerta(1)
    encabezado(
        None,
        "Layout con columnas y métricas",
        "st.set_page_config y st.columns son la base de cualquier panel profesional.",
    )
    codigo_en_vivo(
        """\
# datos: la lista que devuelve la API (lo vimos en la URL)
st.set_page_config(page_title="Panel de IA",
                   page_icon="📊", layout="wide")

top = datos[0]
col1, col2, col3 = st.columns(3)
col1.metric("Líder", top["id"].split("/")[-1], border=True)
col2.metric("Descargas", f'{top["downloads"]:,}', border=True)
col3.metric("Me gusta", top["likes"], border=True)
""",
        apilado=True,
    )
    st.markdown("#### Tres columnas, tres métricas, :yellow-background[cero HTML].")


@slide("2ª compuerta — Gráficos")
def compuerta_2():
    marcador_compuerta(2)
    encabezado(
        None,
        "Gráficos que destacan",
        "Una lista de diccionarios se convierte en un gráfico — y Altair cuida los detalles.",
    )
    codigo_en_vivo(
        """\
import altair as alt

fuente = alt.Data(values=datos)
grafico = alt.Chart(fuente).mark_bar().encode(
    x="downloads:Q",
    y=alt.Y("id:N", sort="-x", title=None,
            axis=alt.Axis(labelLimit=250)),
)
st.altair_chart(grafico)
"""
    )
    st.caption(
        "Para algo rápido: st.bar_chart. También funcionan st.plotly_chart y st.pyplot."
    )


@slide("3ª compuerta — Sidebar y tabs")
def compuerta_3():
    marcador_compuerta(3)
    encabezado(
        None,
        "Sidebar y tabs: organización profesional",
        "Un panel bonito no es solo un gráfico — es información bien organizada.",
    )
    codigo_en_vivo(
        """\
import altair as alt

with st.sidebar:
    st.header("Filtros")
    n = st.slider("Cuántos mostrar", 3, 10, 5)

top = datos[:n]
tab1, tab2 = st.tabs(["📊 Ranking", "📋 Detalle"])
with tab1:
    y = alt.Y("id:N", sort="-x", title=None,
              axis=alt.Axis(labelLimit=250))
    grafico = alt.Chart(alt.Data(values=top))
    st.altair_chart(grafico.mark_bar().encode(
        x="downloads:Q", y=y))
with tab2:
    columnas = ["id", "downloads", "likes"]
    st.dataframe(top, column_order=columnas)
""",
        barra_simulada=True,
    )
    st.caption(
        "En el panel, los filtros viven en la barra lateral de verdad — lo vemos al final."
    )


@slide("4ª compuerta — Interactividad")
def compuerta_4():
    marcador_compuerta(4)
    encabezado(
        None,
        "Interactividad completa",
        "Cada widget es una línea de Python — y el panel reacciona solo.",
    )
    codigo_en_vivo(
        """\
eleccion = st.selectbox("Dataset a monitorear:",
                        [d["id"] for d in datos])
detalle = next(d for d in datos if d["id"] == eleccion)

col1, col2 = st.columns(2)
col1.metric("Descargas", f'{detalle["downloads"]:,}')
col2.metric("Me gusta", detalle["likes"])

cuota = detalle["downloads"] / sum(d["downloads"] for d in datos)
st.progress(cuota, text=f"{cuota:.0%} de las descargas del top 10")
"""
    )


@slide("5ª compuerta — Estado")
def compuerta_5():
    marcador_compuerta(5)
    encabezado(
        None,
        "Estado entre interacciones",
        "Streamlit vuelve a ejecutar todo el script en cada clic — st.session_state es lo que recuerda.",
    )
    codigo_en_vivo(
        """\
if "favoritos" not in st.session_state:
    st.session_state.favoritos = []

eleccion = st.selectbox("Dataset:", [d["id"] for d in datos])
if st.button("⭐ Marcar como favorito"):
    if eleccion not in st.session_state.favoritos:
        st.session_state.favoritos.append(eleccion)

st.write("Favoritos:", st.session_state.favoritos)
"""
    )
    contador, cache = st.columns(2, gap="large", vertical_alignment="center")
    with contador:
        st.metric(
            "Veces que este script se ejecutó desde que abriste la página",
            st.session_state.ejecuciones,
            help="Esta presentación también usa session_state: así sabe en qué slide estamos.",
        )
    with cache:
        st.info(
            "**¿Y la API? No se consulta en cada clic.** `@st.cache_data(ttl=3600)` encima de la "
            "función guarda el resultado por una hora: rápido y sin abusar de la API.",
            icon=":material/cached:",
        )


@slide("6ª compuerta — Tema")
def compuerta_6():
    marcador_compuerta(6)
    encabezado(
        None,
        "Tema visual: el toque final",
        "Un archivo .streamlit/config.toml cambia la cara de toda la app — sin una línea de CSS.",
    )
    izquierda, derecha = st.columns([11, 10], gap="large")
    with izquierda:
        st.markdown(
            ":blue[:material/code:] **`.streamlit/config.toml`** :gray[(el archivo real)]"
        )
        st.code(
            (CARPETA / ".streamlit" / "config.toml").read_text(),
            language="toml",
            wrap_lines=True,
            height=440,
        )
    with derecha, st.container(border=True):
        st.markdown(":orange[:material/play_circle:] **El resultado, en toda la app**")
        with st.container(horizontal=True):
            st.button("Botón primario", type="primary")
            st.button("Botón secundario")
        st.slider("Slider", 0, 100, 60)
        with st.container(horizontal=True):
            st.badge("Azul Python", color="blue")
            st.badge("Amarillo Python", color="yellow")
            st.badge("Fuentes de Google", color="gray")
        st.bar_chart(
            pd.DataFrame(
                {"Texto": [5, 3, 4], "Imagen": [3, 4, 2], "Audio": [2, 2, 3]},
                index=["2024", "2025", "2026"],
            ),
            height=200,
        )


# ---------------------------------------------------------------------------
# Cierre
# ---------------------------------------------------------------------------
@slide("Todo junto", pasos=2)
def todo_junto():
    encabezado(
        "Todo junto",
        "El panel completo",
        "Las 6 compuertas en una sola app — y algunos extras para llevarse a casa.",
        ":material/dashboard:",
    )
    st.page_link("panel.py", label="Abrir el panel", icon=":material/open_in_new:")
    st.space("small")
    c1, c2, c3 = st.columns(3)
    with c1:
        tarjeta(
            "st.column_config",
            "Tablas con barras de progreso, links y listas.",
            ":material/table:",
        )
    with c2:
        tarjeta(
            "on_select",
            "Clic en una fila de la tabla para ver el detalle.",
            ":material/ads_click:",
        )
    with c3:
        tarjeta(
            "st.pills y st.toast",
            "Filtros modernos y avisos que aparecen y desaparecen.",
            ":material/notifications:",
        )
    if aparece(1):
        with st.container(key="paso-1"):
            st.space("small")
            st.warning(
                "**Ojo con los datos: descarga ≠ entrenamiento.** Muchas descargas vienen de pruebas "
                "automáticas — por eso un dataset de imágenes de documentación aparece entre los primeros.",
                icon=":material/visibility:",
            )


@slide("Publicar", pasos=4)
def publicar():
    encabezado("Del laptop al mundo", "Publicando la app", icono=":material/public:")
    st.metric("Tiempo para tener un link público", "< 2 minutos")
    st.markdown(
        "#### `git push` + Streamlit Community Cloud = :yellow-background[link público]"
    )
    pasos = [
        (
            "Sube el código a GitHub",
            "incluido .streamlit/config.toml",
            ":material/upload:",
        ),
        ("Conecta el repo", "en share.streamlit.io", ":material/cable:"),
        ("Comparte el link", "cualquiera lo abre en el navegador", ":material/share:"),
    ]
    for numero, (columna, (titulo, detalle, icono)) in enumerate(
        zip(st.columns(3), pasos), start=1
    ):
        if aparece(numero):
            with columna, st.container(key=f"paso-{numero}", height="stretch"):
                tarjeta(f"{numero}. {titulo}", detalle, f":blue[{icono}]")


@slide("Recapitulando", pasos=2)
def recapitulando():
    encabezado(
        "Recapitulando",
        "El panel que construimos, solo con Python",
        icono=":material/task_alt:",
    )
    for columna, (nombre, detalle, icono) in zip(
        st.columns(3) + st.columns(3), COMPUERTAS
    ):
        with columna, st.container(border=True, height="stretch"):
            st.markdown(f":blue[:material/check_circle:] **{nombre}**")
            st.caption(detalle)
    if aparece(1):
        with st.container(key="paso-1"):
            st.space("small")
            st.markdown(
                "### Ninguna línea de :yellow-background[HTML, CSS o JavaScript]."
            )


@slide("Gracias")
def gracias():
    st.space("large")
    st.title(":yellow-background[¡Gracias!]")
    st.markdown("## ¿Preguntas?")
    st.space("medium")
    with st.container(horizontal=True):
        for nombre, valor in CONTACTO.items():
            if valor:
                st.badge(f"{nombre}: {valor}", color="blue")
    st.space("medium")
    st.markdown(":gray[:material/menu_book: **Para seguir navegando**]")
    links = [
        ("Documentación de Streamlit", "https://docs.streamlit.io"),
        ("Galería de apps", "https://streamlit.io/gallery"),
        ("API de Hugging Face Hub", "https://huggingface.co/docs/hub/api"),
    ]
    if REPO_URL:
        links.insert(0, ("Repositorio de la charla", REPO_URL))
    with st.container(horizontal=True):
        for titulo, url in links:
            st.link_button(titulo, url, icon=":material/open_in_new:")


# ---------------------------------------------------------------------------
# Navegación: el slide actual vive en session_state (¡y en la URL!)
# ---------------------------------------------------------------------------
total = len(SLIDES)

if "slide" not in st.session_state:
    try:
        inicial = int(st.query_params.get("slide", 1)) - 1
    except ValueError:
        inicial = 0
    st.session_state.slide = min(max(inicial, 0), total - 1)
st.session_state.setdefault("paso", 0)


def ir_a(indice: int, paso: int = 0):
    st.session_state.slide = min(max(indice, 0), total - 1)
    st.session_state.paso = paso


def avanzar():
    """→ revela el próximo paso del slide; en el último, pasa al siguiente slide."""
    if st.session_state.paso < SLIDES[st.session_state.slide]["pasos"] - 1:
        st.session_state.paso += 1
    else:
        ir_a(st.session_state.slide + 1)


def retroceder():
    """← oculta el último paso; al inicio, vuelve al slide anterior ya completo."""
    if st.session_state.paso > 0:
        st.session_state.paso -= 1
    elif st.session_state.slide > 0:
        anterior = st.session_state.slide - 1
        ir_a(anterior, paso=SLIDES[anterior]["pasos"] - 1)


actual = st.session_state.slide = min(max(st.session_state.slide, 0), total - 1)
pasos = SLIDES[actual]["pasos"]
paso = st.session_state.paso = min(max(st.session_state.paso, 0), pasos - 1)
st.query_params["slide"] = str(actual + 1)

# La barra lateral lleva los controles de la presentación. Los filtros
# de los ejemplos de código se quedan dentro de cada slide.
with st.sidebar:
    st.header("🎤 Controles")
    st.selectbox(
        "Ir al slide",
        range(total),
        index=actual,
        format_func=lambda i: f"{i + 1}. {SLIDES[i]['titulo']}",
        key=f"saltar_{actual}",
        on_change=lambda: ir_a(st.session_state[f"saltar_{actual}"]),
    )

# Animaciones de entrada (solo en la presentación; el Panel no usa CSS).
# La key cambia en cada slide, así el contenido se vuelve a animar al llegar.
st.html(CARPETA / "assets" / "animaciones.css")
with st.container(key=f"slide-{actual}"):
    SLIDES[actual]["funcion"]()

st.space("medium")
st.divider()
with st.container(horizontal=True, vertical_alignment="center"):
    st.button(
        "Anterior",
        icon=":material/arrow_back:",
        shortcut="Left",
        disabled=actual == 0 and paso == 0,
        on_click=retroceder,
    )
    puntos = " " + "●" * (paso + 1) + "○" * (pasos - paso - 1) if pasos > 1 else ""
    st.progress(
        (actual + 1) / total,
        text=f"{actual + 1} / {total} · {SLIDES[actual]['titulo']}{puntos}",
    )
    st.button(
        "Siguiente",
        icon=":material/arrow_forward:",
        icon_position="right",
        type="primary",
        shortcut="Right",
        disabled=actual == total - 1 and paso == pasos - 1,
        on_click=avanzar,
    )
