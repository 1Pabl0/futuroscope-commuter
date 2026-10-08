"""
Interactive Pydeck Map component for Futuroscope Commuter.
Displays Vitalis bus stops, TER stations, and multimodal transit corridors.
"""
from typing import List, Dict, Any
import pydeck as pdk
import pandas as pd


def render_transit_map(stops: List[Dict[str, Any]]):
    """Renders a 3D/2D interactive Pydeck map with Grand Poitiers & Futuroscope transit network."""
    if not stops:
        return None

    df = pd.DataFrame(stops)

    # Color coding by transport network & type
    def get_color(row):
        if row.get("transport_type") == "train":
            return [168, 85, 247, 220]  # SNCF Purple
        elif row.get("transport_type") == "multimodal":
            return [16, 185, 129, 220]  # Emerald green
        elif "1E" in (row.get("lines") or []):
            return [245, 158, 11, 220]  # Express Orange
        return [14, 165, 233, 200]      # Vitalis Cyan Blue

    df["color"] = df.apply(get_color, axis=1)
    df["radius"] = df["transport_type"].apply(lambda t: 180 if t in ["train", "multimodal"] else 110)
    df["lines_str"] = df["lines"].apply(lambda l: ", ".join(l) if isinstance(l, list) else str(l))

    # Center map between Poitiers and Futuroscope
    view_state = pdk.ViewState(
        latitude=46.6250,
        longitude=0.3520,
        zoom=11.2,
        pitch=35,
        bearing=10
    )

    # Scatter layer for stations
    stops_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color="color",
        get_radius="radius",
        pickable=True,
        opacity=0.9,
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
        get_line_color=[255, 255, 255, 200],
    )

    # Arc layer representing the high-speed 8-min TER shuttle corridor between Poitiers and Futuroscope
    corridor_data = [
        {
            "from_name": "Gare de Poitiers Toumaï",
            "to_name": "Gare du Futuroscope",
            "from_coord": [0.3340, 46.5828],
            "to_coord": [0.3538, 46.6600],
            "color": [168, 85, 247, 180],
        },
        {
            "from_name": "Poitiers Pôle Boncenne (Vitalis 1/1E)",
            "to_name": "Téléport 1 Technopole",
            "from_coord": [0.3412, 46.5815],
            "to_coord": [0.3602, 46.6668],
            "color": [14, 165, 233, 160],
        }
    ]
    corridor_df = pd.DataFrame(corridor_data)

    corridor_layer = pdk.Layer(
        "ArcLayer",
        data=corridor_df,
        get_source_position="from_coord",
        get_target_position="to_coord",
        get_source_color="color",
        get_target_color="color",
        get_width=4,
        pickable=True,
    )

    tooltip = {
        "html": """
        <div style="background-color: #1e293b; color: #f8fafc; padding: 8px 12px; border-radius: 6px; font-family: sans-serif; border: 1px solid #334155;">
            <b style="font-size: 14px; color: #38bdf8;">{name}</b><br/>
            <span style="font-size: 12px; color: #94a3b8;">Zone:</span> <b>{zone}</b><br/>
            <span style="font-size: 12px; color: #94a3b8;">Réseau:</span> <b>{network}</b><br/>
            <span style="font-size: 12px; color: #94a3b8;">Lignes:</span> <code>{lines_str}</code><br/>
            <span style="font-size: 11px; color: #cbd5e1;">🚲 Station vélo: {has_bike_station} | 🚏 Abri: {has_shelter}</span>
        </div>
        """,
        "style": {"color": "white"}
    }

    deck = pdk.Deck(
        layers=[corridor_layer, stops_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/dark-v10" if False else None
    )

    return deck
