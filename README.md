# SiCoGa — Sistema Integral de Gestión Ganadera

Sistema web interno para Chamizal Camperos. Centraliza la operación ganadera reemplazando el control manual en Excel.

## Stack

- Python 3.12
- Django 5.1
- MySQL 8.0
- HTMX + Alpine.js (frontend server-rendered)

## Setup local

```bash
git clone git@github.com:aleph79/SiCoGa.git
cd SiCoGa
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
# Editar .env con credenciales locales de MySQL
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Estructura

- `config/` — settings, URLs, WSGI/ASGI
- `apps/core/` — modelos abstractos y mixins compartidos
- `apps/accounts/` — autenticación, usuarios, roles
- `apps/catalogos/` — catálogos del sistema
- `templates/` — templates Django
- `static/` — CSS y JS

## Ejecución de tests

```bash
pytest
pytest --cov=apps --cov-report=html
```

## Documentación

- Spec del entregable actual: `docs/superpowers/specs/2026-04-29-sicoga-spec-a-cimientos-design.md`
- Plan de implementación: `docs/superpowers/plans/2026-04-29-sicoga-spec-a-cimientos-plan.md`
