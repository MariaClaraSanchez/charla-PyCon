# Monitoreando los datos que entrenan la IA

Charla de **PyCon Panamá 2026** (22 de octubre) — Maria Clara Sanchez.

Una sola app de [Streamlit](https://streamlit.io) con dos páginas:

- 🎤 **Presentación** (`presentacion.py`): los slides de la charla, hechos con Streamlit.
- 📊 **Panel** (`panel.py`): un panel que monitorea los datasets más descargados de [Hugging Face Hub](https://huggingface.co/datasets), construido solo con Python.

No se necesita ninguna clave de API.

## Cómo ejecutarla

Con [Poetry](https://python-poetry.org):

```bash
poetry install
poetry run streamlit run app.py
```

O con `pip`:

```bash
pip install streamlit requests
streamlit run app.py
```

La app se abre en http://localhost:8501.

## El panel, en 6 compuertas

El panel se construye paso a paso durante la charla, como un barco que cruza las compuertas del Canal:

1. **Layout** con columnas y métricas
2. **Gráficos** que destacan
3. **Barra lateral y pestañas** para organizar
4. **Interactividad** completa
5. **Estado** entre interacciones (`st.session_state` y `st.cache_data`)
6. **Tema visual** (`.streamlit/config.toml`)

## Estructura

| Archivo | Qué contiene |
|---|---|
| `app.py` | Punto de entrada: navegación entre las dos páginas |
| `presentacion.py` | Los slides de la charla |
| `panel.py` | El panel de monitoreo |
| `datos.py` | Consulta a la API de Hugging Face, con cache de una hora |
| `.streamlit/config.toml` | Tema con los colores de Python |
| `assets/` | Imágenes, logo y animaciones de los slides |
| `API.md` | Referencia de la API pública de Hugging Face Hub |

## De dónde vienen los datos

El panel consulta un único endpoint público:

```
GET https://huggingface.co/api/datasets?sort=downloads&direction=-1&limit=100
```

La API devuelve **metadatos** (descargas, likes, etiquetas, licencia), no el contenido de los datasets. Más detalles en [API.md](API.md).

## Enlaces

- [Documentación de Streamlit](https://docs.streamlit.io)
- [Galería de apps de Streamlit](https://streamlit.io/gallery)
- [API de Hugging Face Hub](https://huggingface.co/docs/hub/api)
