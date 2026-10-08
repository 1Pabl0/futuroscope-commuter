# Guide de Contribution - Futuroscope Commuter

Merci de contribuer à **Futuroscope Commuter** ! Ce projet a pour ambition de faciliter les déplacements quotidiens de tous les alternants, salariés et étudiants de la Technopole du Futuroscope et du Grand Poitiers.

---

## 🛠️ Configuration de l'Environnement de Développement

### Prérequis
- **Python 3.12+**
- **Docker & Docker Compose** (recommandé pour la stack complète)
- **Git**

### Installation Locale
1. Cloner le projet :
   ```bash
   git clone https://github.com/votre-user/futuroscope-commuter.git
   cd futuroscope-commuter
   ```

2. Créer l'environnement virtuel et installer les dépendances :
   ```bash
   make install
   # Ou manuellement :
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt -r frontend/requirements.txt
   ```

3. Lancer les services :
   - **Backend API (FastAPI) :**
     ```bash
     make run-backend
     # Accessible sur http://localhost:8000/docs
     ```
   - **Frontend (Streamlit) :**
     ```bash
     make run-frontend
     # Accessible sur http://localhost:8501
     ```

---

## 🧪 Tests & Qualité de Code

Toute contribution doit être validée par les tests :

```bash
# Exécution de la suite de tests complète
make test

# Exécution avec rapport de couverture de code
make test-cov
```

Règles de formatage :
- Formateur : **Black** (`black backend frontend`)
- Linter : **Flake8** (`flake8 backend frontend`)

---

## 🔀 Workflow Git & Pull Requests

1. Forkez le projet.
2. Créez votre branche :
   ```bash
   git checkout -b feature/nom-de-fonctionnalite
   ```
3. Commitez vos modifications avec des messages clairs (format conventionnel recommandé, ex: `feat(ict): add wind gusts weighting`).
4. Vérifiez que `make test` passe à 100%.
5. Poussez votre branche et ouvrez une Pull Request vers `main`.
