#!/usr/bin/env bash
# ==============================================================================
# 🚌 Futuroscope Commuter - Script de Lancement Universel
# ==============================================================================
# Usage :
#   ./start.sh              -> Lance Backend + Frontend en local
#   ./start.sh backend      -> Lance uniquement l'API Backend
#   ./start.sh frontend     -> Lance uniquement le Dashboard Frontend
#   ./start.sh docker       -> Déploie la stack complète via Docker Compose
#   ./start.sh test         -> Exécute la suite de tests Pytest
# ==============================================================================

set -e

# Couleurs pour le terminal
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "======================================================================"
    echo "       🚌 FUTUROSCOPE COMMUTER - Technopole du Futuroscope"
    echo "        Plateforme Temps Réel Multi-Modale & Aide à la Décision"
    echo "======================================================================"
    echo -e "${RESET}"
}

check_prerequisites() {
    echo -e "${BLUE}🔍 Vérification de l'environnement...${RESET}"

    # Vérification Python
    if ! command -v python3 &>/dev/null; then
        echo -e "${RED}❌ Erreur : Python 3 n'est pas installé sur votre machine.${RESET}"
        exit 1
    fi

    # Vérification fichier .env
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚙️  Fichier .env absent. Création automatique depuis .env.example...${RESET}"
        cp .env.example .env
    fi

    # Vérification / Création environnement virtuel venv
    if [ ! -d "venv" ] || [ ! -f "venv/bin/uvicorn" ]; then
        echo -e "${YELLOW}📦 Initialisation de l'environnement virtuel Python...${RESET}"
        python3 -m venv venv
        ./venv/bin/pip install --upgrade pip
        ./venv/bin/pip install -r backend/requirements.txt -r frontend/requirements.txt
        echo -e "${GREEN}✅ Environnement prêt !${RESET}"
    fi
}

cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Arrêt des services Futuroscope Commuter en cours...${RESET}"
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    # Nettoyage des éventuels processus résiduels sur les ports 8000 et 8501
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "streamlit run frontend/app.py" 2>/dev/null || true
    echo -e "${GREEN}✨ Services arrêtés proprement. À bientôt !${RESET}"
    exit 0
}

wait_for_backend() {
    echo -e "${BLUE}⏳ Attente de la disponibilité de l'API backend...${RESET}"
    local count=0
    local max=30
    until curl -s http://localhost:8000/api/v1/health &>/dev/null; do
        sleep 0.5
        count=$((count + 1))
        if [ "$count" -ge "$max" ]; then
            echo -e "${RED}❌ Le backend a mis trop de temps à démarrer.${RESET}"
            cleanup
        fi
    done
    echo -e "${GREEN}✅ Backend API prêt et opérationnel !${RESET}"
}

run_local() {
    check_prerequisites
    trap cleanup SIGINT SIGTERM EXIT

    echo -e "${BLUE}🚀 Démarrage du Backend FastAPI (port 8000)...${RESET}"
    PYTHONPATH=backend ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info &
    BACKEND_PID=$!

    # Attendre que l'API soit active
    wait_for_backend

    echo -e "${BLUE}🚀 Démarrage du Dashboard Frontend Streamlit (port 8501)...${RESET}"
    ./venv/bin/streamlit run frontend/app.py \
        --server.port 8501 \
        --server.address 0.0.0.0 \
        --server.headless true \
        --browser.gatherUsageStats false &
    FRONTEND_PID=$!

    sleep 1

    echo ""
    echo -e "${GREEN}${BOLD}======================================================================${RESET}"
    echo -e "${GREEN}${BOLD}           🎉 TOUS LES SERVICES SONT EN LIGNE ET PRÊTS !             ${RESET}"
    echo -e "${GREEN}${BOLD}======================================================================${RESET}"
    echo -e "${BOLD}🌐 Dashboard Visuel :${RESET}          ${CYAN}http://localhost:8501${RESET}"
    echo -e "${BOLD}📑 Documentation API (Swagger) :${RESET} ${CYAN}http://localhost:8000/docs${RESET}"
    echo -e "${BOLD}📖 Documentation ReDoc :${RESET}         ${CYAN}http://localhost:8000/redoc${RESET}"
    echo -e "${BOLD}🏥 Healthcheck Système :${RESET}         ${CYAN}http://localhost:8000/api/v1/health${RESET}"
    echo -e "${GREEN}${BOLD}======================================================================${RESET}"
    echo -e "${YELLOW}Appuyez sur [Ctrl + C] pour arrêter tous les services à tout moment.${RESET}"
    echo ""

    # Ouvrir automatiquement dans le navigateur si sur macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:8501" 2>/dev/null || true
    fi

    # Garder le script actif en attendant les signaux
    wait "$BACKEND_PID" "$FRONTEND_PID"
}

run_backend_only() {
    check_prerequisites
    echo -e "${BLUE}🚀 Démarrage exclusif du Backend FastAPI (port 8000)...${RESET}"
    echo -e "${CYAN}Documentation Swagger : http://localhost:8000/docs${RESET}"
    PYTHONPATH=backend ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

run_frontend_only() {
    check_prerequisites
    echo -e "${BLUE}🚀 Démarrage exclusif du Dashboard Streamlit (port 8501)...${RESET}"
    echo -e "${CYAN}Accès Web : http://localhost:8501${RESET}"
    ./venv/bin/streamlit run frontend/app.py --server.port 8501
}

run_docker() {
    echo -e "${BLUE}🐳 Démarrage de l'infrastructure Docker Compose...${RESET}"
    if ! command -v docker &>/dev/null; then
        echo -e "${RED}❌ Docker n'est pas détecté dans votre PATH.${RESET}"
        echo -e "${YELLOW}💡 Pour lancer sans Docker, utilisez simplement : ./start.sh${RESET}"
        exit 1
    fi
    docker-compose up --build
}

run_tests() {
    check_prerequisites
    echo -e "${BLUE}🧪 Exécution de la suite de tests complète (Pytest)...${RESET}"
    PYTHONPATH=backend ./venv/bin/pytest backend/tests -v
}

# ==============================================================================
# Point d'entrée
# ==============================================================================
print_banner

MODE="${1:-local}"

case "$MODE" in
    local|"")
        run_local
        ;;
    backend)
        run_backend_only
        ;;
    frontend)
        run_frontend_only
        ;;
    docker)
        run_docker
        ;;
    test|tests)
        run_tests
        ;;
    help|--help|-h)
        echo "Commandes disponibles :"
        echo "  ./start.sh          Lance à la fois le backend et le frontend en local"
        echo "  ./start.sh backend  Lance uniquement le serveur backend FastAPI"
        echo "  ./start.sh frontend Lance uniquement le dashboard Streamlit"
        echo "  ./start.sh docker   Lance l'infrastructure via docker-compose"
        echo "  ./start.sh test     Exécute la suite de tests"
        ;;
    *)
        echo -e "${RED}Option inconnue : $MODE${RESET}"
        echo "Utilisez './start.sh help' pour afficher l'aide."
        exit 1
        ;;
esac
