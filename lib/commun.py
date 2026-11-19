"""Éléments partagés par les pages : récepteur AIS unique, météo en cache, indicateurs, tuiles."""
import os

import pandas as pd
import streamlit as st

from lib import direct
from lib.donnees import cppi, mois_fr, serie
from lib.modeles import prevoir, tester


def cle_ais() -> str:
    try:
        return st.secrets["AISSTREAM_API_KEY"]
    except Exception:
        return os.environ.get("AISSTREAM_API_KEY", "")


@st.cache_resource
def recepteur() -> direct.RecepteurAIS:
    """Un seul récepteur AIS pour toute l'application (créé à la première visite)."""
    return direct.RecepteurAIS(cle_ais())


@st.cache_data(ttl=3600, show_spinner="Lecture de la météo…")
def meteo(nom_zone: str) -> dict:
    return direct.meteo(direct.ZONES[nom_zone])


def navires(nom_zone: str) -> tuple:
    """Renvoie (DataFrame des navires, message, secours?)."""
    zone, r = direct.ZONES[nom_zone], recepteur()
    liste = r.navires(zone)
    if liste:
        return pd.DataFrame(liste), None, False
    s = r.secours(zone)
    if s and (r.erreur or time_depuis_depart(r) > 600):
        return pd.DataFrame(s["navires"]), f"flux AIS indisponible, instantané du {s['releve']}", True
    attente = f"écoute démarrée il y a {time_depuis_depart(r) / 60:.0f} min, la liste se complète" if not r.erreur else None
    return pd.DataFrame(), r.erreur or attente, False


def time_depuis_depart(r) -> float:
    import time
    return time.time() - r.depart


def tuile(col, titre, valeur, delta, reference, maj, aide=None, inverse=False):
    with col:
        st.metric(titre, valeur, delta, delta_color="inverse" if inverse else "normal", help=aide, border=True)
        st.caption(f"Réf. : {reference}  \nMàJ : {maj}")


@st.cache_data
def indicateurs_historiques() -> dict:
    lb, la = serie("Long Beach"), serie("Los Angeles")
    commun = lb.dropna().index.intersection(la.dropna().index)
    dernier = commun.max()
    douze = commun[commun > dernier - pd.DateOffset(months=12)]
    an19 = commun[commun.year == 2019]
    prev = prevoir(lb.dropna(), 3)
    mois_prev = prev.mois.iloc[0]
    c = cppi()
    return {
        "dernier": dernier, "lb": lb[dernier], "lb_n1": lb[dernier - pd.DateOffset(years=1)],
        "part": lb[douze].sum() / (lb[douze].sum() + la[douze].sum()) * 100,
        "part19": lb[an19].sum() / (lb[an19].sum() + la[an19].sum()) * 100,
        "prev": prev, "mois_prev": mois_prev, "ref_prev": lb[mois_prev - pd.DateOffset(years=1)],
        "test": tester(lb.dropna(), 12), "cppi": c,
        "maj": f"données à fin {mois_fr(dernier)} (BTS pour LB, port pour LA), récupérées le 19/11/2026",
    }
