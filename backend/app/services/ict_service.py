"""
Indice de Confort de Trajet (ICT) Service.
Predictive algorithm combining real-time multi-modal transit punctuality and localized weather.
"""
import logging
from typing import List, Tuple
from datetime import datetime, timezone
from app.models.schemas import (
    ICTResponse,
    ICTFactorBreakdown,
    WeatherResponse,
    Departure
)

logger = logging.getLogger("futuroscope.ict")


class ICTService:
    @staticmethod
    def calculate_ict(weather: WeatherResponse, bus_departures: List[Departure], ter_departures: List[Departure]) -> ICTResponse:
        """
        Calculates the predictive Trip Comfort Index (0 to 100).
        Fuses meteorological impact and real-time public transit operations.
        """
        w_cur = weather.current
        breakdown: List[ICTFactorBreakdown] = []

        # -------------------------------------------------------------
        # 1. Weather Subscore Evaluation (Base 100)
        # -------------------------------------------------------------
        weather_score = 100

        # Precipitation Impact
        rain = max(w_cur.rain, w_cur.precipitation)
        if rain > 3.0:
            weather_score -= 40
            breakdown.append(ICTFactorBreakdown(
                name="Précipitations",
                score=30,
                impact="Très négatif",
                description=f"Fortes pluies ({rain:.1f} mm/h) - risque de chaussée glissante et visibilité réduite."
            ))
        elif rain > 0.8:
            weather_score -= 22
            breakdown.append(ICTFactorBreakdown(
                name="Précipitations",
                score=60,
                impact="Négatif",
                description=f"Pluie continue ({rain:.1f} mm/h) - vêtements imperméables requis."
            ))
        elif rain > 0.1:
            weather_score -= 10
            breakdown.append(ICTFactorBreakdown(
                name="Précipitations",
                score=80,
                impact="Neutre",
                description="Légères bruines éparses."
            ))
        else:
            breakdown.append(ICTFactorBreakdown(
                name="Précipitations",
                score=100,
                impact="Positif",
                description="Temps sec, chaussée praticable."
            ))

        # Wind & Gusts Impact
        gusts = max(w_cur.wind_gusts, w_cur.wind_speed)
        if gusts > 60:
            weather_score -= 30
            breakdown.append(ICTFactorBreakdown(
                name="Vent & Rafales",
                score=35,
                impact="Très négatif",
                description=f"Rafales tempétueuses ({gusts:.0f} km/h) dangereuses pour les deux-roues."
            ))
        elif gusts > 38:
            weather_score -= 15
            breakdown.append(ICTFactorBreakdown(
                name="Vent & Rafales",
                score=65,
                impact="Négatif",
                description=f"Vent soutenu ({gusts:.0f} km/h) provoquant une résistance accrue."
            ))
        else:
            breakdown.append(ICTFactorBreakdown(
                name="Vent & Rafales",
                score=95,
                impact="Positif",
                description=f"Vent calme à modéré ({gusts:.0f} km/h)."
            ))

        # Temperature Impact
        temp = w_cur.temperature
        if temp < 2.0:
            weather_score -= 15
            breakdown.append(ICTFactorBreakdown(
                name="Température",
                score=50,
                impact="Négatif",
                description=f"Température proche du gel ({temp:.1f}°C) - risque de verglas localisé."
            ))
        elif temp < 7.0:
            weather_score -= 8
            breakdown.append(ICTFactorBreakdown(
                name="Température",
                score=75,
                impact="Neutre",
                description=f"Temps froid ({temp:.1f}°C) - gants et écharpe recommandés."
            ))
        elif temp > 32.0:
            weather_score -= 15
            breakdown.append(ICTFactorBreakdown(
                name="Température",
                score=55,
                impact="Négatif",
                description=f"Forte chaleur ({temp:.1f}°C) - pensez à vous hydrater."
            ))
        else:
            breakdown.append(ICTFactorBreakdown(
                name="Température",
                score=100,
                impact="Positif",
                description=f"Température idéale ({temp:.1f}°C) pour les déplacements."
            ))

        weather_score = max(10, min(100, weather_score))

        # -------------------------------------------------------------
        # 2. Transit Subscore Evaluation (Base 100)
        # -------------------------------------------------------------
        transit_score = 100
        all_deps = bus_departures + ter_departures

        if all_deps:
            total_delays = sum(d.delay_minutes for d in all_deps)
            avg_delay = total_delays / len(all_deps)
            cancelled_count = sum(1 for d in all_deps if d.status == "CANCELLED")

            # Penalties on delays
            if avg_delay > 8:
                transit_score -= 35
                breakdown.append(ICTFactorBreakdown(
                    name="Ponctualité Réseau",
                    score=40,
                    impact="Très négatif",
                    description=f"Retards conséquents constatés (moyenne {avg_delay:.1f} min)."
                ))
            elif avg_delay >= 2:
                transit_score -= 18
                breakdown.append(ICTFactorBreakdown(
                    name="Ponctualité Réseau",
                    score=70,
                    impact="Négatif",
                    description=f"Légers ralentissements sur le réseau (moyenne {avg_delay:.1f} min)."
                ))
            else:
                breakdown.append(ICTFactorBreakdown(
                    name="Ponctualité Réseau",
                    score=95,
                    impact="Positif",
                    description="Trafic fluide sur les lignes Vitalis et TER Nouvelle-Aquitaine."
                ))

            if cancelled_count > 0:
                transit_score -= 25 * cancelled_count
                breakdown.append(ICTFactorBreakdown(
                    name="Suppressions",
                    score=30,
                    impact="Très négatif",
                    description=f"{cancelled_count} départ(s) annulé(s) sur le créneau."
                ))
        else:
            transit_score = 85

        transit_score = max(10, min(100, transit_score))

        # -------------------------------------------------------------
        # 3. Overall Weighted ICT Score
        # -------------------------------------------------------------
        global_score = int(round(0.50 * weather_score + 0.50 * transit_score))
        global_score = max(5, min(100, global_score))

        level, badge_label, color_hex = ICTService._get_level_metadata(global_score)

        # -------------------------------------------------------------
        # 4. Multimodal Recommendations & Commuter Advice
        # -------------------------------------------------------------
        recommended_mode, alternative_mode, advice, equipment = ICTService._generate_commuter_tips(
            global_score, weather_score, transit_score, w_cur, ter_departures
        )

        summary_text = (
            f"Indice de {global_score}/100 ({badge_label}). "
            f"Météo: {w_cur.weather_description} ({w_cur.temperature:.1f}°C). "
            f"{'Réseaux de transport parfaitement synchronisés.' if transit_score >= 80 else 'Ralentissements signalés sur les axes principaux.'}"
        )

        return ICTResponse(
            score=global_score,
            level=level,
            badge_label=badge_label,
            color_hex=color_hex,
            summary=summary_text,
            weather_subscore=weather_score,
            transit_subscore=transit_score,
            breakdown=breakdown,
            recommended_mode=recommended_mode,
            alternative_mode=alternative_mode,
            commuter_advice=advice,
            equipment_suggestions=equipment,
            updated_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def _get_level_metadata(score: int) -> Tuple[str, str, str]:
        if score >= 85:
            return "EXCELLENT", "Trajet Idéal", "#10B981"   # Emerald Green
        if score >= 70:
            return "BON", "Trajet Fluide", "#06B6D4"        # Cyan Blue
        if score >= 50:
            return "MOYEN", "Conditions Modérées", "#F59E0B" # Amber
        if score >= 30:
            return "DIFFICILE", "Trajet Dégradé", "#EF4444" # Orange-Red
        return "PERTURBÉ", "Forte Perturbation", "#B91C1C"  # Dark Red

    @staticmethod
    def _generate_commuter_tips(
        global_score: int,
        weather_score: int,
        transit_score: int,
        w_cur,
        ter_departures: List[Departure]
    ) -> Tuple[str, str, List[str], List[str]]:
        advice: List[str] = []
        equipment: List[str] = []

        has_rain = (w_cur.rain > 0.2) or (w_cur.precipitation > 0.2)
        has_high_wind = (w_cur.wind_gusts > 40) or (w_cur.wind_speed > 30)

        # Mode Selection
        if not has_rain and not has_high_wind and weather_score >= 75:
            rec_mode = "🚲 Mobilité Douce (Vélo / Trottinette - Réseau Cyclable Technopole)"
            alt_mode = "🚌 Bus Vitalis Ligne 1E Express"
            advice.append("Excellentes conditions pour le vélo : trajet vivifiant le long de la voie verte.")
            equipment.append("Casque & gilet haute visibilité")
        elif has_rain or has_high_wind:
            rec_mode = "🚆 Navette TER Nouvelle-Aquitaine (8 min Poitiers ↔ Futuroscope)"
            alt_mode = "🚌 Bus Vitalis Ligne 1 (Pôle Boncenne - LPI)"
            advice.append("Intempéries détectées : la navette TER vous évite la pluie et les ralentissements routiers.")
            equipment.append("Parapluie robuste ou veste imperméable")
        else:
            rec_mode = "🚌 Bus Vitalis Ligne 1 ou 1E Express"
            alt_mode = "🚆 TER Nouvelle-Aquitaine"
            advice.append("Fréquences régulières toutes les 10-15 min sur la ligne 1 Vitalis.")
            equipment.append("Titre de transport / Pass Vitalis")

        # Additional specific alerts
        if ter_departures:
            next_ter = ter_departures[0]
            if next_ter.status != "CANCELLED":
                advice.append(f"Prochaine navette TER dans {next_ter.minutes_left} min ({next_ter.destination}).")

        if w_cur.temperature < 6.0:
            equipment.append("Gants et bonnet thermique")
        elif w_cur.temperature > 28.0:
            equipment.append("Gourde d'eau fraîche & lunettes de soleil")

        return rec_mode, alt_mode, advice, equipment
