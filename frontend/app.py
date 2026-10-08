"""
Futuroscope Commuter - Main Streamlit Dashboard Application.
"""
import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

from components.map import render_transit_map
from components.ict_gauge import render_ict_gauge
from components.widgets import render_weather_widget, render_departures_cards, render_service_status

# Page setup
st.set_page_config(
    page_title="Futuroscope Commuter",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")


@st.cache_data(ttl=15)
def fetch_overview():
    try:
        resp = requests.get(f"{BACKEND_URL}/overview", timeout=4.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=30)
def fetch_stops():
    try:
        resp = requests.get(f"{BACKEND_URL}/transit/stops", timeout=3.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


def run_simulation(temp: float, rain: float, wind: float, bus_delay: int, ter_cancelled: bool):
    payload = {
        "temperature": temp,
        "rain_mm": rain,
        "wind_gusts_kmh": wind,
        "avg_bus_delay_min": bus_delay,
        "ter_cancelled": ter_cancelled
    }
    try:
        resp = requests.post(f"{BACKEND_URL}/ict/simulate", json=payload, timeout=3.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        st.error(f"Erreur simulation : {e}")
    return None


def main():
    # Header Banner
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, #0284c7 0%, #0369a1 50%, #0f172a 100%);
                    padding: 20px 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h1 style="margin: 0; font-size: 28px; color: #ffffff; font-weight: 800;">
                        🚌 Futuroscope Commuter
                    </h1>
                    <p style="margin: 4px 0 0 0; font-size: 14px; color: #e0f2fe;">
                        Plateforme temps réel multi-modale (Bus Vitalis, TER Nouvelle-Aquitaine & Météo) pour la <b>Technopole du Futuroscope (Grand Poitiers)</b>
                    </p>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 8px 14px; border-radius: 8px; text-align: right;">
                    <span style="font-size: 11px; color: #f0f9ff; text-transform: uppercase; font-weight: 600;">Dernière synchro</span><br/>
                    <b style="color: #ffffff; font-size: 14px;">{}</b>
                </div>
            </div>
        </div>
        """.format(datetime.now().strftime("%H:%M:%S")),
        unsafe_allow_html=True
    )

    # Fetch live overview from backend
    data = fetch_overview()

    if not data:
        st.warning("⚠️ Connexion directe au backend en cours de synchronisation...")
        st.info("Astuce : Lancez le backend avec `uvicorn app.main:app --reload` dans le dossier `backend`.")
        return

    ict_data = data.get("ict", {})
    weather_data = data.get("weather", {})
    vitalis_buses = data.get("next_vitalis_buses", [])
    ter_trains = data.get("next_ter_trains", [])
    stops = data.get("key_stops", [])
    service_status = data.get("service_status", {})

    # Sidebar Controls
    st.sidebar.image("https://img.shields.io/badge/Futuroscope-Technopole_Commuter-0284c7?style=for-the-badge", use_container_width=True)
    st.sidebar.markdown("### 🧭 Paramètres de Trajet")
    direction = st.sidebar.radio(
        "Sens de déplacement :",
        ["Poitiers ➔ Technopole Futuroscope (Aller)", "Technopole Futuroscope ➔ Poitiers (Retour)"],
        index=0
    )

    stop_filter = st.sidebar.selectbox(
        "Pôle d'arrêt favori :",
        ["Tous les arrêts clés", "Téléport 1", "Téléport 4 (ISAE-ENSMA)", "Gare du Futuroscope", "Gare de Poitiers Toumaï"]
    )

    if st.sidebar.button("🔄 Actualiser les données en direct", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    render_service_status(service_status)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 11px; color: #94a3b8; line-height: 1.4;">
            <b>Projet Open Source &bull; Grand Poitiers</b><br/>
            Sources : Open Data Grand Poitiers / Vitalis (GTFS-RT), SNCF Réseau, Open-Meteo Vienne (86).
        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Tableau de Bord (Live)",
        "🗺️ Carte Interactive du Réseau",
        "🧠 Simulateur Prédictif (ICT)",
        "🔌 Documentation & API"
    ])

    # -------------------------------------------------------------
    # TAB 1: Live Commuter Dashboard
    # -------------------------------------------------------------
    with tab1:
        st.markdown("### 🧠 Indice de Confort de Trajet (ICT)")
        render_ict_gauge(ict_data)

        st.markdown("---")

        # Departures Section
        col_bus, col_ter = st.columns(2)
        with col_bus:
            st.markdown("### 🚌 Prochains Bus Vitalis (Ligne 1, 1E Express)")
            st.caption("Pôles Téléport, LPI, Boncenne & Gare Toumaï")
            render_departures_cards(vitalis_buses, network="vitalis")

        with col_ter:
            st.markdown("### 🚆 Navette TER Nouvelle-Aquitaine (8 min direct)")
            st.caption("Gare de Poitiers Toumaï ↔ Halte Passerelle Futuroscope")
            render_departures_cards(ter_trains, network="sncf_ter")

        st.markdown("---")

        # Weather Section
        st.markdown("### 🌤️ Conditions Météo & Prévisions Locales")
        render_weather_widget(weather_data)

    # -------------------------------------------------------------
    # TAB 2: Interactive Map
    # -------------------------------------------------------------
    with tab2:
        st.markdown("### 🗺️ Cartographie Multi-Modale du Couloir Poitiers ↔ Futuroscope")
        st.caption("Visualisez les arrêts Vitalis, la halte TER du Futuroscope, les stations vélos et la navette rapide.")
        
        map_deck = render_transit_map(stops)
        if map_deck:
            st.pydeck_chart(map_deck)

        st.markdown("#### 🚏 Répertoire des Arrêts et Équipements")
        if stops:
            df_stops = pd.DataFrame(stops)[["name", "network", "zone", "lines", "has_bike_station", "has_shelter"]]
            df_stops.columns = ["Nom de l'Arrêt", "Réseau", "Zone", "Lignes desservies", "Station Vélo 🚲", "Abri voyageur 🚏"]
            st.dataframe(df_stops, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 3: ICT Prediction Simulator
    # -------------------------------------------------------------
    with tab3:
        st.markdown("### 🧠 Simulateur d'Aide à la Décision (Indice de Confort de Trajet)")
        st.write(
            "Testez comment l'algorithme prédictif réagit aux aléas météorologiques et aux perturbations de circulation "
            "pour réorienter les salariés et étudiants vers le meilleur mode de transport."
        )

        sim_c1, sim_c2 = st.columns(2)
        with sim_c1:
            st.markdown("##### 🌧️ Scénario Météorologique")
            sim_temp = st.slider("Température (°C)", min_value=-5.0, max_value=38.0, value=12.0, step=0.5)
            sim_rain = st.slider("Intensité de pluie (mm/h)", min_value=0.0, max_value=8.0, value=2.5, step=0.5)
            sim_wind = st.slider("Rafales de vent (km/h)", min_value=5.0, max_value=85.0, value=42.0, step=1.0)

        with sim_c2:
            st.markdown("##### 🚦 Scénario Transports en Commun")
            sim_delay = st.slider("Retard moyen des bus Vitalis (minutes)", min_value=0, max_value=25, value=6, step=1)
            sim_cancel = st.checkbox("Simuler une suppression sur la navette TER", value=False)

        sim_result = run_simulation(sim_temp, sim_rain, sim_wind, sim_delay, sim_cancel)

        if sim_result:
            st.markdown("---")
            st.markdown("#### 🎯 Résultat de la Simulation")
            render_ict_gauge(sim_result)

            st.markdown("##### 🔍 Détail des Pénalités et Facteurs Détectés :")
            breakdown = sim_result.get("breakdown", [])
            for item in breakdown:
                impact = item.get("impact")
                icon = "🔴" if "Très" in impact else ("🟠" if "Négatif" in impact else "🟢")
                st.markdown(f"- {icon} **{item.get('name')}** (Score: {item.get('score')}/100) : {item.get('description')}")

    # -------------------------------------------------------------
    # TAB 4: API Documentation
    # -------------------------------------------------------------
    with tab4:
        st.markdown("### 🔌 API REST & Architecture Microservices")
        st.markdown(
            f"""
            L'API backend est construite avec **FastAPI**, asynchrone et entièrement documentée nativement :
            - 📖 **Documentation Swagger UI :** [http://localhost:8000/docs](http://localhost:8000/docs)
            - 📑 **Documentation ReDoc :** [http://localhost:8000/redoc](http://localhost:8000/redoc)
            - 🏥 **Healthcheck Endpoint :** `GET /api/v1/health`
            - 🕒 **Vitalis Bus Departures :** `GET /api/v1/transit/vitalis/departures`
            - 🚆 **TER Navette Departures :** `GET /api/v1/transit/ter/departures`
            - 🌤️ **Open-Meteo Vienne :** `GET /api/v1/weather`
            - 🧠 **Calcul ICT en direct :** `GET /api/v1/ict/current`
            """
        )

        st.code("""
# Exemple de requête cURL pour récupérer l'ICT en temps réel
curl -X GET "http://localhost:8000/api/v1/ict/current" -H "accept: application/json"
        """, language="bash")


if __name__ == "__main__":
    main()
