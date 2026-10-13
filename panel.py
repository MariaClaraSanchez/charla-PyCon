"""
Panel de Monitoreo de Datos de Entrenamiento de IA
---------------------------------------------------
PyCon Panamá - Maria Clara Sanchez

Panel construido en 6 compuertas, siguiendo la charla:
  1) Layout con columnas y métricas
  2) Gráficos que destacan
  3) Sidebar y tabs (organización profesional)
  4) Interactividad completa
  5) Estado entre interacciones (session_state y cache de datos)
  6) Tema visual (ver .streamlit/config.toml)

No se necesita ninguna clave de API.

Esta es la página "Panel" de app.py.
"""

from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from datos import cargar_datos

# ---------------------------------------------------------------------------
# Datos como insumo, con cache (ver datos.py; se explica en la 5ª compuerta)
# ---------------------------------------------------------------------------
try:
    datos = cargar_datos()
except requests.RequestException as error:
    st.error(f"No se pudieron buscar los datos ahora: {error}")
    st.stop()

if datos.empty:
    st.warning("La API no devolvió ningún dataset.")
    st.stop()


# ---------------------------------------------------------------------------
# 5ª compuerta (preparación) - el estado sobrevive entre interacciones
# ---------------------------------------------------------------------------
if "favoritos" not in st.session_state:
    st.session_state.favoritos = []


def alternar_favorito(dataset_id: str):
    favoritos = st.session_state.favoritos
    if dataset_id in favoritos:
        favoritos.remove(dataset_id)
        st.toast(f"Quitado de favoritos: {dataset_id}", icon="🗑️")
    else:
        favoritos.append(dataset_id)
        st.toast(f"Agregado a favoritos: {dataset_id}", icon="⭐")


# ---------------------------------------------------------------------------
# 3ª compuerta - sidebar: los controles viven a un costado
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Controles")

    top_n = st.slider(
        "Tamaño del ranking",
        min_value=10,
        max_value=len(datos),
        value=min(50, len(datos)),
        step=10,
        help="Cuántos de los datasets más descargados analizar.",
    )

    opciones_modalidad = sorted(datos["modalidad"].unique())
    modalidades_elegidas = st.pills(
        "Modalidad",
        opciones_modalidad,
        selection_mode="multi",
        default=opciones_modalidad,
    )

    busqueda = st.text_input("Buscar por nombre o autor", placeholder="ej. openai")

    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.subheader(f"⭐ Favoritos ({len(st.session_state.favoritos)})")
    if st.session_state.favoritos:
        for fav in st.session_state.favoritos:
            st.markdown(f"- `{fav}`")
    else:
        st.caption("Marca datasets en la pestaña *Explorar*.")

    st.divider()
    st.caption(
        "**¿Qué estoy viendo?** Los datasets públicos más descargados de "
        "[Hugging Face Hub](https://huggingface.co/datasets) en los últimos 30 días: "
        "los datos con los que hoy se entrenan y evalúan modelos de IA."
    )

# Aplicamos los filtros del sidebar
filtrado = datos.head(top_n)
filtrado = filtrado[filtrado["modalidad"].isin(modalidades_elegidas or [])]
if busqueda:
    filtrado = filtrado[filtrado["id"].str.contains(busqueda, case=False)]


# ---------------------------------------------------------------------------
# 1ª compuerta - encabezado, contexto y métricas
# ---------------------------------------------------------------------------
st.title("📊 ¿Con qué datos se entrena la IA hoy?")
st.markdown(
    "Panel de monitoreo de los datasets más usados de **Hugging Face Hub**, "
    "el repositorio abierto donde la comunidad publica datos para entrenar modelos."
)
with st.container(horizontal=True):
    st.badge("Datos en vivo", icon=":material/sensors:", color="green")
    st.badge("API pública de Hugging Face", icon=":material/hub:")
    st.badge(
        f"Consultado a las {datetime.now():%H:%M}",
        icon=":material/schedule:",
        color="gray",
    )

if filtrado.empty:
    st.warning("Ningún dataset coincide con los filtros. Intenta ampliar la búsqueda.")
    st.stop()

lider = filtrado.iloc[0]
total_descargas = int(filtrado["descargas"].sum())


def mas_comun(columna: str, vacio: str) -> tuple[str, float]:
    """Valor más frecuente, ignorando los datasets sin etiqueta."""
    etiquetados = filtrado[filtrado[columna] != vacio][columna]
    if etiquetados.empty:
        return "-", 0.0
    valor = etiquetados.value_counts().idxmax()
    return valor, (etiquetados == valor).mean()


modalidad_top, cuota_modalidad = mas_comun("modalidad", "Sin etiqueta")
licencia_top, cuota_licencia = mas_comun("licencia", "Sin licencia")

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Descargas (30 días)",
    f"{total_descargas / 1e6:,.1f} M",
    help="Suma de descargas del último mes de los datasets filtrados.",
    border=True,
    chart_data=filtrado["descargas"].tolist(),
    chart_type="bar",
)
col2.metric("Líder del ranking", lider["nombre"], help=lider["id"], border=True)
col3.metric(
    "Modalidad dominante",
    modalidad_top,
    f"{cuota_modalidad:.0%} de los etiquetados",
    delta_color="off",
    delta_arrow="off",
    border=True,
)
col4.metric(
    "Licencia más común",
    licencia_top,
    f"{cuota_licencia:.0%} de los etiquetados",
    delta_color="off",
    delta_arrow="off",
    border=True,
)


# ---------------------------------------------------------------------------
# 3ª compuerta - tabs: cada pregunta en su propia pestaña
# ---------------------------------------------------------------------------
tab_ranking, tab_composicion, tab_explorar, tab_favoritos = st.tabs(
    ["🏆 Ranking", "🧩 Composición", "🔎 Explorar", "⭐ Favoritos"]
)

# ---------------------------------------------------------------------------
# 2ª compuerta - gráficos que destacan
# ---------------------------------------------------------------------------
with tab_ranking:
    izquierda, derecha = st.columns([3, 2], gap="large")

    with izquierda:
        st.subheader("Los 15 más descargados")
        st.caption("Descargas en los últimos 30 días.")
        st.bar_chart(
            filtrado.head(15),
            x="nombre",
            y="descargas",
            color="modalidad",
            horizontal=True,
            sort="-descargas",
            x_label="",
            y_label="Descargas",
            height=480,
        )

    with derecha:
        st.subheader("¿Popular = usado?")
        st.caption(
            "Cada punto es un dataset. Muchos likes no siempre significan muchas descargas."
        )
        st.scatter_chart(
            filtrado,
            x="descargas",
            y="likes",
            color="modalidad",
            x_label="Descargas",
            y_label="Likes",
            height=480,
        )


def contar(columna: str, top: int = 8) -> pd.DataFrame:
    """Cuenta valores de una columna de listas (ej. tareas, idiomas)."""
    conteo = filtrado[columna].explode().dropna().value_counts().head(top)
    return conteo.rename_axis("categoria").reset_index(name="datasets")


with tab_composicion:
    st.subheader("¿Qué tipo de datos dominan?")
    st.caption("Distribución por etiquetas que los autores asignan a cada dataset.")

    c1, c2 = st.columns(2, gap="large")
    with c1, st.container(border=True):
        st.markdown("**Modalidades**")
        st.bar_chart(
            contar("modalidades"),
            x="categoria",
            y="datasets",
            horizontal=True,
            sort="-datasets",
            x_label="",
            y_label="",
        )
    with c2, st.container(border=True):
        st.markdown("**Tareas**")
        st.bar_chart(
            contar("tareas"),
            x="categoria",
            y="datasets",
            horizontal=True,
            sort="-datasets",
            x_label="",
            y_label="",
        )

    c3, c4 = st.columns(2, gap="large")
    with c3, st.container(border=True):
        st.markdown("**Idiomas**")
        st.bar_chart(
            contar("idiomas"),
            x="categoria",
            y="datasets",
            horizontal=True,
            sort="-datasets",
            x_label="",
            y_label="",
        )
    with c4, st.container(border=True):
        st.markdown("**Licencias**")
        licencias = filtrado["licencia"].value_counts().head(8)
        licencias = licencias.rename_axis("categoria").reset_index(name="datasets")
        st.bar_chart(
            licencias,
            x="categoria",
            y="datasets",
            horizontal=True,
            sort="-datasets",
            x_label="",
            y_label="",
        )


# ---------------------------------------------------------------------------
# 4ª compuerta - interactividad completa
# ---------------------------------------------------------------------------
with tab_explorar:
    st.subheader("Explora el ranking")
    st.caption("👆 Haz clic en una fila para ver la ficha del dataset.")

    seleccion = st.dataframe(
        filtrado,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_order=[
            "posicion",
            "id",
            "descargas",
            "likes",
            "modalidades",
            "licencia",
            "creado",
            "url",
        ],
        column_config={
            "posicion": st.column_config.NumberColumn("#", width="small"),
            "id": st.column_config.TextColumn("Dataset", width="large"),
            "descargas": st.column_config.ProgressColumn(
                "Descargas (30 días)",
                format="compact",
                min_value=0,
                max_value=int(datos["descargas"].max()),
            ),
            "likes": st.column_config.NumberColumn("❤️ Likes", format="compact"),
            "modalidades": st.column_config.ListColumn("Modalidades"),
            "licencia": "Licencia",
            "creado": st.column_config.DateColumn("Creado", format="MMM YYYY"),
            "url": st.column_config.LinkColumn("Enlace", display_text="Abrir ↗"),
        },
    )

    filas = seleccion.selection.rows
    elegido = filtrado.iloc[filas[0]] if filas else lider

    with st.container(border=True):
        cabecera, acciones = st.columns([3, 2], vertical_alignment="center")
        with cabecera:
            st.subheader(elegido["id"])
            with st.container(horizontal=True):
                for m in elegido["modalidades"]:
                    st.badge(m, color="blue")
                st.badge(elegido["licencia"], icon=":material/gavel:", color="gray")
        with acciones, st.container(horizontal=True, horizontal_alignment="right"):
            es_favorito = elegido["id"] in st.session_state.favoritos
            st.button(
                "Quitar de favoritos" if es_favorito else "Marcar como favorito",
                icon="⭐",
                type="secondary" if es_favorito else "primary",
                on_click=alternar_favorito,
                args=(elegido["id"],),
            )
            st.link_button(
                "Ver en Hugging Face", elegido["url"], icon=":material/open_in_new:"
            )

        m1, m2, m3 = st.columns(3)
        m1.metric(
            "Posición global",
            f"#{elegido['posicion']}",
            f"de {len(datos)}",
            delta_color="off",
            delta_arrow="off",
        )
        m2.metric("Descargas (30 días)", f"{elegido['descargas']:,}")
        m3.metric("Likes", f"{elegido['likes']:,}")

        cuota = elegido["descargas"] / total_descargas
        st.progress(cuota, text=f"Representa el {cuota:.1%} de las descargas del panel")

        if elegido["tareas"]:
            st.markdown("**Tareas:** " + ", ".join(elegido["tareas"]))

        with st.expander("Ver respuesta cruda de la API (JSON)"):
            st.json(elegido["crudo"], expanded=False)


# ---------------------------------------------------------------------------
# 5ª compuerta - estado entre interacciones
# ---------------------------------------------------------------------------
with tab_favoritos:
    favoritos = datos[datos["id"].isin(st.session_state.favoritos)]
    if favoritos.empty:
        st.info(
            "Todavía no marcaste favoritos. Ve a **🔎 Explorar** y elige algunos.",
            icon="⭐",
        )
    else:
        st.subheader("Comparando tus favoritos")
        st.caption("Esta lista sobrevive a cada clic gracias a `st.session_state`.")
        st.bar_chart(
            favoritos, x="nombre", y=["descargas", "likes"], stack=False, x_label=""
        )
        if st.button("Limpiar favoritos", icon=":material/delete:"):
            st.session_state.favoritos = []
            st.rerun()


# ---------------------------------------------------------------------------
# 6ª compuerta - tema visual: ver .streamlit/config.toml
# (colores de Python aplicados sin tocar este archivo)
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Construido en vivo en la PyCon Panamá con Streamlit + la API pública de Hugging Face Hub · "
    "100% Python, sin HTML, CSS ni JavaScript."
)
