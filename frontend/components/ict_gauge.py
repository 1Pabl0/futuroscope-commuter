"""
ICT Visual Gauge and Mobility Recommendation Component.
"""
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any


def render_ict_gauge(ict_data: Dict[str, Any]):
    """Renders a modern, visually striking gauge and breakdown for the Trip Comfort Index."""
    score = ict_data.get("score", 75)
    level = ict_data.get("level", "BON")
    badge_label = ict_data.get("badge_label", "Trajet Fluide")
    color = ict_data.get("color_hex", "#06B6D4")
    w_sub = ict_data.get("weather_subscore", 80)
    t_sub = ict_data.get("transit_subscore", 85)

    col1, col2 = st.columns([1.1, 1.9])

    with col1:
        # Plotly Half-Donut Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 42, "color": color, "family": "Inter, sans-serif"}},
            title={"text": f"<b>{badge_label}</b>", "font": {"size": 18, "color": "#E2E8F0"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#475569"},
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "#1E293B",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 30], "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [30, 50], "color": "rgba(249, 115, 22, 0.15)"},
                    {"range": [50, 70], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [70, 85], "color": "rgba(6, 182, 212, 0.15)"},
                    {"range": [85, 100], "color": "rgba(16, 185, 129, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#F8FAFC", "width": 3},
                    "thickness": 0.75,
                    "value": score
                }
            }
        ))
        fig.update_layout(
            height=240,
            margin=dict(l=20, r=20, t=35, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Mini subscore badges
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            st.metric("🌤️ Sous-score Météo", f"{w_sub}/100")
        with sub_c2:
            st.metric("🚆 Sous-score Trafic", f"{t_sub}/100")

    with col2:
        # Recommendation Cards
        rec_mode = ict_data.get("recommended_mode", "Bus Vitalis Ligne 1")
        alt_mode = ict_data.get("alternative_mode", "TER Nouvelle-Aquitaine")

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                        border-left: 5px solid {color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;
                        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; font-weight: 700;">
                    Mode de déplacement recommandé pour votre trajet
                </div>
                <div style="font-size: 18px; font-weight: 700; color: #f8fafc; margin-top: 4px;">
                    {rec_mode}
                </div>
                <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">
                    <b>Alternative de secours :</b> {alt_mode}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Practical advice
        advice_list = ict_data.get("commuter_advice", [])
        if advice_list:
            for item in advice_list:
                st.info(f"💡 {item}")

        # Equipment tags
        equip = ict_data.get("equipment_suggestions", [])
        if equip:
            tags_html = " ".join([
                f"<span style='background-color: #334155; color: #e2e8f0; padding: 4px 10px; border-radius: 12px; font-size: 12px; margin-right: 6px;'>🎒 {e}</span>"
                for e in equip
            ])
            st.markdown(f"<div style='margin-top: 6px;'><b>Équipement conseillé :</b> {tags_html}</div>", unsafe_allow_html=True)
