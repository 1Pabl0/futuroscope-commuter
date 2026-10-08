# 🚌 Futuroscope Commuter API & Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](docker-compose.yml)
[![Tests Status](https://img.shields.io/badge/Tests-20%20Passed%20(100%25)-brightgreen.svg)]()

**Futuroscope Commuter** est une plateforme open-source (API REST + Dashboard interactif) conçue pour optimiser les trajets quotidiens des salariés, alternants et étudiants vers la **Technopole du Futuroscope (Grand Poitiers)**. 

En croisant en temps réel les données de transport multi-modal (Bus Vitalis, navette ferroviaire TER Nouvelle-Aquitaine) et les prévisions météo locales à haute résolution, l'application fournit un **Indice de Confort de Trajet (ICT)** et des recommandations d'aide à la décision pour fluidifier les déplacements et encourager la mobilité douce.

---

## ✨ Fonctionnalités Principales

- 🕒 **Temps Réel Multi-Modal :** 
  - Agrégation des prochains passages de bus (Lignes Vitalis 1, 1E Express, 21, Navette E) avec estimation des retards et affluence.
  - Horaires en direct de la **navette ferroviaire TER Nouvelle-Aquitaine** (Gare de Poitiers Toumaï ↔ Gare du Futuroscope en seulement **8 minutes** de trajet direct).
- 🌤️ **Contextualisation Météo :** 
  - Prévisions météo horaires géolocalisées pour la Technopole (Chasseneuil-du-Poitou / Jaunay-Marigny, Vienne 86).
  - Alertes automatiques de précipitations, températures extrêmes et rafales de vent.
- 🧠 **Indice de Confort de Trajet (ICT) :** 
  - Algorithme prédictif scoré de 0 à 100 combinant la régularité du trafic et les intempéries.
  - Recommandation dynamique du mode de déplacement optimal (vélo / trottinette sur pistes cyclables, bus express 1E, ou navette TER abritée) avec conseils d'équipement.
- 🗺️ **Cartographie Interactive 3D / 2D :** 
  - Visualisation des arrêts de bus, stations TER, stations vélos en libre-service et du corridor multimodal Poitiers-Futuroscope via Pydeck.
- 🎯 **Simulateur de Trajet :** 
  - Interface interactive permettant de tester la réaction de l'algorithme face à des scénarios météo extrêmes ou des pannes de réseau.
- 🐳 **Prêt pour la Production :** 
  - Déploiement en une seule commande via Docker Compose (PostgreSQL/PostGIS, Redis, FastAPI, Streamlit).
  - Mode local sans Docker avec fallback SQLite et cache en mémoire à tolérance de panne.

---

## 🏗️ Architecture Technique

```
                              ┌────────────────────────────────────────┐
                              │     Sources Open Data Publiques        │
                              │  - Open-Meteo API (Vienne 86)          │
                              │  - Grand Poitiers / Vitalis (GTFS-RT)   │
                              │  - SNCF Réseau (TER Nouvelle-Aquitaine) │
                              └───────────────────┬────────────────────┘
                                                  │
                                                  ▼
┌──────────────────────┐              ┌────────────────────────┐              ┌──────────────────────┐
│  Dashboard Streamlit │ ◄──────────► │  Backend FastAPI (REST)│ ◄──────────► │  Redis & PostgreSQL  │
│  (Port 8501)         │  HTTP / JSON │  (Port 8000)           │              │  (PostGIS / Cache)   │
└──────────────────────┘              └────────────────────────┘              └──────────────────────┘
```

- **Backend :** FastAPI (Python 3.12) - Asynchrone, typage strict Pydantic v2, documentation OpenAPI/Swagger native.
- **Frontend :** Streamlit avec visualisations dynamiques Plotly et cartographie Pydeck.
- **Base de Données & Cache :** 
  - PostgreSQL avec extension spatiale **PostGIS** pour la localisation des arrêts (fallback SQLite automatique en local).
  - **Redis** pour la mise en cache avec expiration TTL (fallback mémoire transparente si Redis indisponible).

---

## 🚀 Démarrage Rapide

### Option 1 : Déploiement via Docker Compose (Recommandé)

Assurez-vous d'avoir [Docker](https://docker.com) et [Docker Compose](https://docker.com) installés.

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/votre-user/futuroscope-commuter.git
   cd futuroscope-commuter
   ```

2. **Configurer l'environnement :**
   ```bash
   cp .env.example .env
   ```

3. **Lancer tous les conteneurs :**
   ```bash
   docker-compose up --build
   ```

- 🌐 **Dashboard Web :** `http://localhost:8501`
- 📑 **Documentation API Swagger :** `http://localhost:8000/docs`
- 📖 **Documentation ReDoc :** `http://localhost:8000/redoc`

---

### Option 2 : Exécution Locale en Mode Développement (Sans Docker)

1. **Initialiser l'environnement virtuel :**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt -r frontend/requirements.txt
   ```

2. **Lancer les tests unitaires :**
   ```bash
   make test
   # Ou : PYTHONPATH=backend pytest backend/tests -v
   ```

3. **Démarrer l'API Backend :**
   ```bash
   make run-backend
   # Le serveur démarre sur http://localhost:8000
   ```

4. **Démarrer le Dashboard Frontend (dans un autre terminal) :**
   ```bash
   make run-frontend
   # Le tableau de bord s'ouvre sur http://localhost:8501
   ```

---

## 🔌 Points d'Accès de l'API REST (Endpoints)

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/overview` | Synthèse complète pour le tableau de bord (ICT, météo, bus, TER) |
| `GET` | `/api/v1/ict/current` | Indice de Confort de Trajet en temps réel |
| `POST` | `/api/v1/ict/simulate` | Simulation personnalisée de l'algorithme ICT |
| `GET` | `/api/v1/transit/stops` | Liste géolocalisée de tous les arrêts (Vitalis & TER) |
| `GET` | `/api/v1/transit/vitalis/departures` | Prochains passages de bus Vitalis |
| `GET` | `/api/v1/transit/ter/departures` | Prochains passages de la navette TER Poitiers-Futuroscope |
| `GET` | `/api/v1/weather` | Données météo actuelles et prévisions horaires (Technopole) |
| `GET` | `/api/v1/health` | Vérification de l'état de santé du système et des connecteurs |

---

## 🧠 Algorithme de l'Indice de Confort de Trajet (ICT)

L'ICT est une note prédictive sur **100** calculée en temps réel selon deux axes :

$$\text{ICT} = 0.50 \times \text{Score Météo} + 0.50 \times \text{Score Trafic}$$

- **Sous-score Météo :**
  - Pénalité pluie : $-10$ à $-40$ pts selon l'intensité en mm/h.
  - Pénalité vent / rafales : $-15$ à $-30$ pts si rafales $> 38$ km/h.
  - Températures extrêmes : Pénalité gel ($< 2^\circ\text{C}$) ou canicule ($> 32^\circ\text{C}$).
- **Sous-score Trafic :**
  - Retards constatés en minutes sur les lignes Vitalis et TER.
  - Détection des suppressions de trains/bus ($-25$ pts par départ annulé).
- **Règles d'orientation :**
  - **Score $\ge 85$ (Idéal) :** Encouragement de la mobilité douce (vélo, trottinette le long de la voie verte).
  - **Intempéries / Pluie continue :** Recommandation automatique de la navette TER (8 min abritée).
  - **Heures de pointe régulières :** Bus Vitalis Ligne 1E Express.

---

## 🧪 Tests et Intégration Continue

Le projet dispose d'une suite de 20 tests unitaires et d'intégration validant le comportement de chaque service :
```bash
./setup_and_test.sh
```

Un pipeline CI [GitHub Actions](.github/workflows/ci.yml) exécute automatiquement les tests et les vérifications de linting (**Black**, **Flake8**) à chaque commit.

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Pour proposer une amélioration ou corriger un problème :
1. Consultez le guide [CONTRIBUTING.md](CONTRIBUTING.md).
2. Créez votre branche (`git checkout -b feature/ma-fonctionnalite`).
3. Soumettez une Pull Request vers la branche `main`.

---

## 📄 Licence

Distribué sous la licence **MIT**. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.

---

## 👤 Contact

**Paul Girault** - Étudiant Ingénieur à l'**EFREI Paris** (Recherche d'alternance à Poitiers)
- **LinkedIn :** [linkedin.com/in/paulgirault](https://linkedin.com)
- **GitHub :** [github.com/paulgirault](https://github.com)
