.PHONY: help install test test-cov run-backend run-frontend dev docker-up docker-down clean

help:
	@echo "Futuroscope Commuter - Commandes disponibles:"
	@echo "  make install       Installe les dépendances virtuelles"
	@echo "  make test          Exécute les tests unitaires et d'intégration"
	@echo "  make test-cov      Exécute les tests avec rapport de couverture"
	@echo "  make run-backend   Lance le serveur FastAPI (port 8000)"
	@echo "  make run-frontend  Lance le dashboard Streamlit (port 8501)"
	@echo "  make dev           Lance les services en local"
	@echo "  make docker-up     Déploie la stack complète (PostGIS, Redis, Backend, Frontend)"
	@echo "  make docker-down   Arrête les conteneurs Docker"

install:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r backend/requirements.txt -r frontend/requirements.txt

test:
	PYTHONPATH=backend ./venv/bin/pytest backend/tests -v

test-cov:
	PYTHONPATH=backend ./venv/bin/pytest backend/tests -v --cov=app --cov-report=term-missing

run-backend:
	PYTHONPATH=backend ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	./venv/bin/streamlit run frontend/app.py --server.port 8501

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage futuroscope.db
