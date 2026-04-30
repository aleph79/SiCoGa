.PHONY: help install migrate migrations run shell superuser test test-cov lint lint-check clean

PY := python
MANAGE := $(PY) manage.py

help:
	@echo "SiCoGa — comandos comunes"
	@echo
	@echo "  make install      Instala deps de dev y pre-commit hooks"
	@echo "  make migrate      Aplica migraciones"
	@echo "  make migrations   Genera migraciones nuevas"
	@echo "  make run          Levanta runserver en :8000"
	@echo "  make shell        Abre shell de Django"
	@echo "  make superuser    Crea superuser interactivo"
	@echo "  make test         Corre la suite de pytest"
	@echo "  make test-cov     Corre pytest con reporte HTML de cobertura en htmlcov/"
	@echo "  make lint         Aplica black + isort y reporta flake8"
	@echo "  make lint-check   Sólo verifica formato sin modificar"
	@echo "  make clean        Borra __pycache__, .pytest_cache, htmlcov"

install:
	pip install --upgrade pip
	pip install -r requirements/dev.txt
	pre-commit install

migrate:
	$(MANAGE) migrate

migrations:
	$(MANAGE) makemigrations

run:
	$(MANAGE) runserver

shell:
	$(MANAGE) shell

superuser:
	$(MANAGE) createsuperuser

test:
	pytest -q

test-cov:
	pytest --cov=apps --cov-report=html --cov-report=term
	@echo "Reporte HTML en htmlcov/index.html"

lint:
	black .
	isort .
	flake8 .

lint-check:
	black --check .
	isort --check-only .
	flake8 .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
