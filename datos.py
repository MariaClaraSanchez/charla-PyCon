"""
Datos compartidos entre el panel y la presentación.

Una sola función con cache para no consultar la API en cada clic.
"""

import pandas as pd
import requests
import streamlit as st

HF_DATASETS_URL = "https://huggingface.co/api/datasets"

MODALIDADES = {
    "text": "Texto",
    "image": "Imagen",
    "audio": "Audio",
    "video": "Video",
    "tabular": "Tabular",
    "timeseries": "Series temporales",
    "3d": "3D",
    "geospatial": "Geoespacial",
    "document": "Documento",
}


def con_prefijo(tags: list[str], prefijo: str) -> list[str]:
    """Extrae valores de tags tipo 'modality:text' -> ['text']."""
    return [t.split(":", 1)[1] for t in tags if t.startswith(prefijo + ":")]


@st.cache_data(ttl=3600, show_spinner="Consultando Hugging Face Hub…")
def cargar_datos(limit: int = 100) -> pd.DataFrame:
    """Busca los datasets más descargados en Hugging Face Hub.

    La API es pública, no exige clave ni registro.
    Documentación: https://huggingface.co/docs/hub/api
    """
    params = {"sort": "downloads", "direction": -1, "limit": limit}
    respuesta = requests.get(HF_DATASETS_URL, params=params, timeout=10)
    respuesta.raise_for_status()

    filas = []
    for posicion, d in enumerate(respuesta.json(), start=1):
        tags = d.get("tags", [])
        modalidades = [MODALIDADES.get(m, m) for m in con_prefijo(tags, "modality")]
        licencias = con_prefijo(tags, "license")
        filas.append(
            {
                "posicion": posicion,
                "id": d["id"],
                "nombre": d["id"].split("/")[-1],
                "autor": d.get("author", "-"),
                "descargas": d.get("downloads", 0),
                "likes": d.get("likes", 0),
                "modalidades": modalidades,
                "modalidad": modalidades[0] if modalidades else "Sin etiqueta",
                "tareas": con_prefijo(tags, "task_categories"),
                "idiomas": con_prefijo(tags, "language"),
                "licencia": licencias[0] if licencias else "Sin licencia",
                "creado": pd.to_datetime(d.get("createdAt")),
                "url": f"https://huggingface.co/datasets/{d['id']}",
                "crudo": d,
            }
        )
    return pd.DataFrame(filas)
