"""
Tableau de bord portuaire – vu depuis un terminal de Long Beach.
Lancer :  streamlit run app.py
Clé aisstream.io : dans .streamlit/secrets.toml (local) ou dans Settings → Secrets (Streamlit Cloud),
sous le nom AISSTREAM_API_KEY. Elle n'est jamais écrite dans le code.
"""
import streamlit as st

st.set_page_config(page_title="Terminal Long Beach – tableau de bord", page_icon="🏗️", layout="wide")

pages = [
    st.Page("views/synthese.py", title="Synthèse", icon="📋", default=True),
    st.Page("views/volumes.py", title="Volumes LA & LB", icon="📦"),
    st.Page("views/benchmark.py", title="Comparaison mondiale", icon="🌍"),
    st.Page("views/temps_reel.py", title="Temps réel", icon="📡"),
    st.Page("views/sources.py", title="Sources & méthode", icon="📚"),
]
st.navigation(pages).run()
