"""
Monitoreando los Datos que Entrenan la IA
-----------------------------------------
PyCon Panamá - Maria Clara Sanchez

Una sola app de Streamlit con dos páginas:
  🎤 Presentación - los slides de la charla, hechos con Streamlit (presentacion.py)
  📊 Panel        - el panel de monitoreo que construimos (panel.py)

No se necesita ninguna clave de API.

Ejecutar localmente:
    pip install streamlit requests
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Datos que entrenan la IA",
    page_icon="📊",
    layout="wide",
)
st.logo("assets/python-logo.svg", size="large", link="https://www.python.org")

pagina = st.navigation(
    [
        st.Page("presentacion.py", title="Presentación", icon="🎤", default=True),
        st.Page("panel.py", title="Panel", icon="📊"),
    ],
    position="top",
)
pagina.run()
