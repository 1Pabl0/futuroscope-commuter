"""
Reusable widgets for weather charts, departures tables, and live badges.
"""
from typing import List, Dict, Any
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_weather_widget(weather: Dict[str, Any]):
    """Renders current weather cards and hourly temperature & rain forecast."""
    current = weather.get("current", {})
    hourly = weather.get("hourly", [])

    # Main Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="🌡️ Température",
            value=f"{current.get('temperature', 0):.1f}°C",
            delta=f"Ressenti {current.get('apparent_temperature', 0):.1f}°C",
            delta_color="off"
        )
    with m2:
        st.metric(
            label="🌧️ Précipitations",
            value=f"{current.get('precipitation', 0):.1f} mm/h",
            delta="Sec" if current.get("precipitation", 0) == 0 else "Pluie en cours",
            delta_color="normal" if current.get("precipitation", 0) == 0 else "inverse"
        )
    with m3:
        st.metric(
            label="💨 Vent & Rafales",
            value=f"{current.get('wind_speed', 0):.0f} km/h",
            delta=f"Pointes à {current.get('wind_gusts', 0):.0f} km/h",
            delta_color="off"
        )
    with m4:
        st.metric(
            label="🌤️ Ciel",
            value=f"{current.get('weather_icon', '⛅')} {current.get('weather_description', 'Variable')}",
            delta=current.get("comfort_category", "Normal"),
            delta_color="off"
        )

    # Weather Alerts
    alerts = weather.get("alerts", [])
    for alert in alerts:
        st.warning(alert)

    # Hourly Forecast Chart
    if hourly:
        df_h = pd.DataFrame(hourly)
        fig = go.Figure()

        # Temp Line
        fig.add_trace(go.Scatter(
            x=df_h["time"],
            y=df_h["temperature"],
            mode="lines+markers",
            name="Température (°C)",
            line=dict(color="#38BDF8", width=3),
            marker=dict(size=6)
        ))

        # Rain Prob Bar
        fig.add_trace(go.Bar(
            x=df_h["time"],
            y=df_h["precipitation_probability"],
            name="Risque de pluie (%)",
            marker=dict(color="rgba(14, 165, 233, 0.3)"),
            yaxis="y2"
        ))

        fig.update_layout(
            title="<b>Prévisions Horaires (Prochaines Heures - Technopole)</b>",
            height=260,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Temp (°C)", showgrid=True, gridcolor="#334155"),
            yaxis2=dict(title="Pluie (%)", overlaying="y", side="right", range=[0, 100], showgrid=False),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)


def render_departures_cards(departures: List[Dict[str, Any]], network: str):
    """Renders upcoming bus or train departures with real-time badges."""
    if not departures:
        st.info("Aucun départ prévu sur ce créneau.")
        return

    for dep in departures:
        status = dep.get("status", "ON_TIME")
        delay = dep.get("delay_minutes", 0)
        mins_left = dep.get("minutes_left", 0)
        line = dep.get("line", "")
        dest = dep.get("destination", "")
        planned = dep.get("planned_time", "")
        stop_name = dep.get("stop_name", "")

        # Status badge styling
        if status == "CANCELLED":
            badge_color = "#ef4444"
            badge_text = "SUPPRIMÉ"
            time_display = "---"
        elif delay > 0:
            badge_color = "#f59e0b"
            badge_text = f"+{delay} min"
            time_display = f"dans {mins_left} min"
        else:
            badge_color = "#10b981"
            badge_text = "À L'HEURE"
            time_display = f"dans {mins_left} min" if mins_left > 0 else "À l'approche"

        # Card container
        line_badge_color = "#a855f7" if network == "sncf_ter" else "#0284c7"
        if line == "1E":
            line_badge_color = "#f97316"

        st.markdown(
            f"""
            <div style="background-color: #1e293b; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;
                        display: flex; justify-content: space-between; align-items: center; border: 1px solid #334155;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background-color: {line_badge_color}; color: white; font-weight: 800; font-size: 14px;
                                border-radius: 6px; padding: 4px 10px; min-width: 45px; text-align: center;">
                        {line}
                    </div>
                    <div>
                        <div style="font-weight: 600; font-size: 15px; color: #f8fafc;">{dest}</div>
                        <div style="font-size: 12px; color: #94a3b8;">
                            🚏 {stop_name} &bull; Horaires: <span style="color: #cbd5e1;">{planned}</span>
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 17px; font-weight: 700; color: #38bdf8;">{time_display}</div>
                    <span style="background-color: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color};
                                 padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700;">
                        {badge_text}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_service_status(service_status: Dict[str, str]):
    """Renders small system status badges in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔌 État des Connecteurs Open Data")
    for key, val in service_status.items():
        name = key.replace("_", " ").title()
        if val in ["OPERATIONAL", "CONNECTED", "SYNCHRONIZED", "ACTIVE"]:
            st.sidebar.markdown(f"🟢 **{name}** : En ligne")
        else:
            st.sidebar.markdown(f"🟡 **{name}** : {val}")
