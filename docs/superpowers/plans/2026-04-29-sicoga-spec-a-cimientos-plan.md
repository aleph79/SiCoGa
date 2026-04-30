# SiCoGa — Spec A: Cimientos — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dejar el proyecto Django operativo con auth, 4 roles, 6 catálogos con CRUD completo, motor de Programa de Reimplantes precargado, auditoría con `simple_history`, CI básico y pre-commit.

**Architecture:** Proyecto Django 5.1 con apps separadas (`core`, `accounts`, `catalogos`), templates server-side con HTMX + Alpine, MySQL 8.0, single-tenant. CSS portado del dummy v4 (dark mode con design tokens). Borrado lógico (`activo=False`). Auditoría automática vía `django-simple-history`.

**Tech Stack:** Python 3.12 · Django 5.1 · MySQL 8.0.46 · mysqlclient · django-simple-history · django-environ · pytest-django · factory-boy · HTMX 1.9 · Alpine.js 3 · gunicorn · whitenoise · GitHub Actions

**Spec:** `docs/superpowers/specs/2026-04-29-sicoga-spec-a-cimientos-design.md`

**Working dir:** `/Users/zeus/Documents/Fuentes/Django/SiCoGa`

**Convención de commits:** prefijo Conventional Commits (`feat:`, `chore:`, `test:`, `docs:`, `ci:`).

---

## Plan de archivos a crear/modificar

```
SiCoGa/
├── .github/workflows/ci.yml                    # Task 7
├── .gitignore                                   # Task 1
├── .env.example                                 # Task 3
├── .pre-commit-config.yaml                      # Task 6
├── .flake8                                      # Task 6
├── .coveragerc                                  # Task 5
├── pyproject.toml                               # Task 6
├── pytest.ini                                   # Task 5
├── manage.py                                    # Task 3
├── README.md                                    # Tasks 1, 33
├── requirements/{base,dev,prod}.txt             # Task 2
├── config/                                      # Task 3
│   ├── settings/{base,dev,prod}.py
│   ├── urls.py, wsgi.py, asgi.py
├── apps/
│   ├── core/                                    # Task 8
│   ├── accounts/                                # Tasks 9-13
│   └── catalogos/                               # Tasks 18-31
├── templates/
│   ├── base.html, partials/                     # Task 15
│   ├── 4xx/5xx pages                            # Task 16
│   ├── dashboard/home.html                      # Task 17
│   ├── accounts/                                # Tasks 11-12
│   └── catalogos/                               # Tasks 19-27
├── static/css/sicoga.css, js/sicoga.js          # Task 14
└── tests/conftest.py, factories.py              # Task 5
```

---

## Phase 1 — Foundation (Tasks 1–7)

### Task 1: Initialize repo, virtualenv, .gitignore, README skeleton

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `venv/` (virtualenv local — NO se commitea)

**Steps:**

- [ ] **Step 1.1: Verify working directory and initialize git**

```bash
cd /Users/zeus/Documents/Fuentes/Django/SiCoGa
git init
git remote add origin git@github.com:aleph79/SiCoGa.git
git branch -M main
```

Expected: `.git/` directory created, remote configured.

- [ ] **Step 1.2: Create `.gitignore`**

Create `/Users/zeus/Documents/Fuentes/Django/SiCoGa/.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtualenv
venv/
env/
ENV/
.venv/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment
.env
.env.local

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
.coverage.*
htmlcov/
.pytest_cache/
.tox/
coverage.xml
*.cover

# Pre-commit
.pre-commit-cache/
```

- [ ] **Step 1.3: Create initial README.md**

Create `/Users/zeus/Documents/Fuentes/Django/SiCoGa/README.md`:

```markdown
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
```

- [ ] **Step 1.4: Create virtualenv**

```bash
cd /Users/zeus/Documents/Fuentes/Django/SiCoGa
python3.12 -m venv venv
source venv/bin/activate
python --version
```

Expected: `Python 3.12.x`. PyCharm: en Settings → Project → Python Interpreter, seleccionar `./venv/bin/python`.

- [ ] **Step 1.5: First commit**

```bash
cd /Users/zeus/Documents/Fuentes/Django/SiCoGa
git add .gitignore README.md
git status
git commit -m "chore: initialize repo with gitignore and readme skeleton"
```

Expected: commit creado, `venv/` ignorado.

---

### Task 2: Define dependencies (requirements/)

**Files:**
- Create: `requirements/base.txt`
- Create: `requirements/dev.txt`
- Create: `requirements/prod.txt`

**Steps:**

- [ ] **Step 2.1: Create `requirements/base.txt`**

```
Django>=5.1,<5.2
mysqlclient>=2.2,<2.3
django-simple-history>=3.7,<3.8
django-environ>=0.11,<0.12
openpyxl>=3.1,<3.2
```

- [ ] **Step 2.2: Create `requirements/dev.txt`**

```
-r base.txt

pytest>=8.0,<9.0
pytest-django>=4.8,<5.0
pytest-cov>=5.0,<6.0
factory-boy>=3.3,<4.0
coverage>=7.6,<8.0
black>=24.10,<25.0
isort>=5.13,<6.0
flake8>=7.1,<8.0
pre-commit>=3.8,<4.0
django-debug-toolbar>=4.4,<5.0
ipython>=8.27,<9.0
```

- [ ] **Step 2.3: Create `requirements/prod.txt`**

```
-r base.txt

gunicorn>=23.0,<24.0
whitenoise>=6.7,<7.0
```

- [ ] **Step 2.4: Install dev deps**

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/dev.txt
```

Expected: `Successfully installed Django-5.1.x mysqlclient-2.2.x ...`. Si `mysqlclient` falla en macOS, instalar primero el driver del sistema:

```bash
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="$(brew --prefix mysql-client)/lib/pkgconfig"
pip install mysqlclient
```

- [ ] **Step 2.5: Verify Django installed**

```bash
python -c "import django; print(django.get_version())"
```

Expected: `5.1.x`.

- [ ] **Step 2.6: Commit**

```bash
git add requirements/
git commit -m "chore: pin python dependencies for base/dev/prod"
```

---

### Task 3: Bootstrap Django project with split settings

**Files:**
- Create: `config/__init__.py`
- Create: `config/settings/__init__.py`
- Create: `config/settings/base.py`
- Create: `config/settings/dev.py`
- Create: `config/settings/prod.py`
- Create: `config/urls.py`
- Create: `config/wsgi.py`
- Create: `config/asgi.py`
- Create: `manage.py`
- Create: `.env.example`
- Create: `apps/__init__.py`

**Steps:**

- [ ] **Step 3.1: Run `django-admin startproject`**

```bash
cd /Users/zeus/Documents/Fuentes/Django/SiCoGa
source venv/bin/activate
django-admin startproject config .
```

Expected: crea `manage.py`, `config/__init__.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`.

- [ ] **Step 3.2: Convert `config/settings.py` to a package**

```bash
mkdir config/settings
mv config/settings.py config/settings/base.py
touch config/settings/__init__.py
```

- [ ] **Step 3.3: Edit `config/settings/base.py`** (replace entire file content)

```python
"""Base settings for SiCoGa. Inherited by dev and prod."""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-key-change-in-prod")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "simple_history",
    # local apps (registered as Tasks add them)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "accounts:login"
```

- [ ] **Step 3.4: Create `config/settings/dev.py`**

```python
"""Development settings."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE  # noqa: F405

INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
```

- [ ] **Step 3.5: Create `config/settings/prod.py`**

```python
"""Production settings."""
from .base import *  # noqa: F401,F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

ADMINS = [("Admin", env("ADMIN_EMAIL", default="admin@example.com"))]  # noqa: F405

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "sicoga.log",  # noqa: F405
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["file", "mail_admins"], "level": "WARNING"},
    },
}
```

- [ ] **Step 3.6: Create `.env.example`**

```bash
# Django
DEBUG=True
SECRET_KEY=replace-me-with-a-long-random-string
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.dev

# Database
DATABASE_URL=mysql://sicoga_user:sicoga_pass@127.0.0.1:3306/sicoga_dev

# Email (prod)
ADMIN_EMAIL=admin@example.com
```

- [ ] **Step 3.7: Update `manage.py` to default to dev settings**

Edit `manage.py` line `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")` →

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
```

- [ ] **Step 3.8: Update `config/wsgi.py` and `config/asgi.py` similarly**

Replace `config.settings` with `config.settings.prod` in both files.

- [ ] **Step 3.9: Update `config/urls.py`** (placeholder dashboard)

```python
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="dashboard/home.html"), name="dashboard-home-stub"),
]
```

> Nota: el namespace `dashboard:home` se conecta cuando se cree la app dashboard en Spec F. Por ahora el `name=` es un stub.

- [ ] **Step 3.10: Create `apps/__init__.py`**

```bash
mkdir -p apps && touch apps/__init__.py
```

- [ ] **Step 3.11: Create local `.env` from template**

```bash
cp .env.example .env
# Editar .env con la cadena de conexión real al MySQL local
```

- [ ] **Step 3.12: Commit**

```bash
git add config/ manage.py apps/__init__.py .env.example
git commit -m "feat: bootstrap django project with split settings"
```

---

### Task 4: Create MySQL database and verify connection

**Files:** none (DB setup)

**Steps:**

- [ ] **Step 4.1: Create database and user in MySQL**

```bash
mysql -u root -p
```

```sql
CREATE DATABASE sicoga_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sicoga_user'@'localhost' IDENTIFIED BY 'sicoga_pass';
GRANT ALL PRIVILEGES ON sicoga_dev.* TO 'sicoga_user'@'localhost';
CREATE DATABASE sicoga_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON sicoga_test.* TO 'sicoga_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

- [ ] **Step 4.2: Update `.env` with real credentials**

```bash
DATABASE_URL=mysql://sicoga_user:sicoga_pass@127.0.0.1:3306/sicoga_dev
```

- [ ] **Step 4.3: Run `check`**

```bash
source venv/bin/activate
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 4.4: Run initial Django migrations**

```bash
python manage.py migrate
```

Expected: aplica las migraciones de `auth`, `contenttypes`, `sessions`, `admin`, `simple_history` sin errores.

- [ ] **Step 4.5: Smoke test runserver**

```bash
python manage.py runserver
```

Visitar `http://127.0.0.1:8000/admin/`. Expected: pantalla de login del admin.

`Ctrl+C` para detener.

- [ ] **Step 4.6: Commit (.env should be ignored)**

```bash
git status
# .env NO debe aparecer
git diff
# Debería ser limpio
```

No commit en este paso (sólo verificación de DB).

---

### Task 5: Set up testing infrastructure (pytest, factories, coverage)

**Files:**
- Create: `pytest.ini`
- Create: `.coveragerc`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/factories.py`
- Create: `tests/test_smoke.py`

**Steps:**

- [ ] **Step 5.1: Create `pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
python_files = test_*.py tests.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = -ra --strict-markers --tb=short
markers =
    slow: marks tests as slow
testpaths = tests apps
```

- [ ] **Step 5.2: Create `.coveragerc`**

```ini
[run]
source = apps
omit =
    */migrations/*
    */tests/*
    */admin.py
    */apps.py
    */urls.py

[report]
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == .__main__.:
fail_under = 85
show_missing = True
```

- [ ] **Step 5.3: Create `tests/__init__.py`**

```bash
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 5.4: Create `tests/conftest.py`**

```python
"""Global pytest fixtures."""
import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Allow all tests to use the DB without re-declaring `db` fixture."""
    pass
```

- [ ] **Step 5.5: Create `tests/factories.py` (placeholder; modelos llegan en tasks posteriores)**

```python
"""Factory-boy factories for SiCoGa models."""
# Las factories se irán añadiendo conforme se creen los modelos.
```

- [ ] **Step 5.6: Create smoke test**

`tests/test_smoke.py`:

```python
"""Smoke tests for project bootstrap."""
import django


def test_django_version_is_5_1():
    assert django.get_version().startswith("5.1")


def test_settings_loaded():
    from django.conf import settings

    assert settings.LANGUAGE_CODE == "es-mx"
    assert settings.TIME_ZONE == "America/Mexico_City"
    assert settings.USE_TZ is True
```

- [ ] **Step 5.7: Run smoke tests**

```bash
source venv/bin/activate
DATABASE_URL='mysql://sicoga_user:sicoga_pass@127.0.0.1:3306/sicoga_test' \
  pytest tests/test_smoke.py -v
```

Expected: 2 PASS.

- [ ] **Step 5.8: Commit**

```bash
git add pytest.ini .coveragerc tests/
git commit -m "test: configure pytest, coverage and smoke tests"
```

---

### Task 6: Set up linting (black, isort, flake8) and pre-commit

**Files:**
- Create: `pyproject.toml`
- Create: `.flake8`
- Create: `.pre-commit-config.yaml`

**Steps:**

- [ ] **Step 6.1: Create `pyproject.toml`**

```toml
[tool.black]
line-length = 100
target-version = ["py312"]
extend-exclude = '''
/(
  | migrations
  | venv
  | staticfiles
)/
'''

[tool.isort]
profile = "black"
line_length = 100
known_django = "django"
known_third_party = ["pytest", "factory", "environ", "simple_history"]
sections = ["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
skip = ["migrations", "venv", "staticfiles"]
```

- [ ] **Step 6.2: Create `.flake8`**

```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503, E501
exclude =
    .git,
    __pycache__,
    venv,
    staticfiles,
    */migrations/*,
    config/settings/dev.py,
    config/settings/prod.py
per-file-ignores =
    __init__.py: F401
```

- [ ] **Step 6.3: Create `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        language_version: python3.12
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: check-yaml
      - id: check-toml
```

- [ ] **Step 6.4: Install pre-commit hooks**

```bash
source venv/bin/activate
pre-commit install
```

Expected: `pre-commit installed at .git/hooks/pre-commit`.

- [ ] **Step 6.5: Run pre-commit on all files**

```bash
pre-commit run --all-files
```

Expected: pasa o aplica auto-fixes (black/isort). Si hay cambios, re-stage:

```bash
git add -A
```

- [ ] **Step 6.6: Commit**

```bash
git add pyproject.toml .flake8 .pre-commit-config.yaml
git commit -m "chore: configure black, isort, flake8 and pre-commit hooks"
```

---

### Task 7: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

**Steps:**

- [ ] **Step 7.1: Create CI workflow**

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: sicoga_test
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping --silent"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements/dev.txt

      - name: Install system deps
        run: |
          sudo apt-get update
          sudo apt-get install -y default-libmysqlclient-dev pkg-config build-essential

      - name: Install python deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements/dev.txt

      - name: Wait for MySQL
        run: |
          for i in {1..30}; do
            mysqladmin ping -h 127.0.0.1 -P 3306 -uroot -proot && break
            sleep 1
          done

      - name: Run linters
        run: |
          black --check .
          isort --check .
          flake8 .

      - name: Run migrations
        env:
          DJANGO_SETTINGS_MODULE: config.settings.dev
          SECRET_KEY: ci-test-secret
          DEBUG: "False"
          ALLOWED_HOSTS: "*"
          DATABASE_URL: mysql://root:root@127.0.0.1:3306/sicoga_test
        run: python manage.py migrate

      - name: Run tests with coverage
        env:
          DJANGO_SETTINGS_MODULE: config.settings.dev
          SECRET_KEY: ci-test-secret
          DEBUG: "False"
          ALLOWED_HOSTS: "*"
          DATABASE_URL: mysql://root:root@127.0.0.1:3306/sicoga_test
        run: pytest --cov=apps --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
```

- [ ] **Step 7.2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add github actions workflow with mysql service"
```

> Después del primer push se valida en GitHub que el CI pase en verde.

---

## Phase 2 — Core app (Task 8)

### Task 8: Core app with abstract models

**Files:**
- Create: `apps/core/__init__.py`
- Create: `apps/core/apps.py`
- Create: `apps/core/models.py`
- Create: `apps/core/mixins.py`
- Create: `apps/core/tests/__init__.py`
- Create: `apps/core/tests/test_models.py`
- Modify: `config/settings/base.py` (registrar `apps.core` en INSTALLED_APPS)

**Steps:**

- [ ] **Step 8.1: Create `apps/core/` skeleton**

```bash
mkdir -p apps/core/tests
touch apps/core/__init__.py
touch apps/core/tests/__init__.py
```

- [ ] **Step 8.2: Create `apps/core/apps.py`**

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = "Core"
```

- [ ] **Step 8.3: Register in `INSTALLED_APPS`**

Edit `config/settings/base.py`, append after `"simple_history",`:

```python
    # local apps
    "apps.core",
```

- [ ] **Step 8.4: Write failing tests for abstract models**

`apps/core/tests/test_models.py`:

```python
"""Tests for abstract models. Uses a temporary concrete model declared in test."""
import pytest
from django.db import connection, models

from apps.core.models import AuditableModel, TimeStampedModel


class _ConcreteTimeStamped(TimeStampedModel):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = "core"


class _ConcreteAuditable(AuditableModel):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = "core"


@pytest.fixture(autouse=True)
def create_test_tables():
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(_ConcreteTimeStamped)
        schema_editor.create_model(_ConcreteAuditable)
    yield
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(_ConcreteAuditable)
        schema_editor.delete_model(_ConcreteTimeStamped)


def test_timestamped_sets_created_and_updated():
    obj = _ConcreteTimeStamped.objects.create(name="x")
    assert obj.created_at is not None
    assert obj.updated_at is not None


def test_auditable_default_activo_is_true():
    obj = _ConcreteAuditable.objects.create(name="x")
    assert obj.activo is True


def test_auditable_inherits_timestamps():
    obj = _ConcreteAuditable.objects.create(name="x")
    assert obj.created_at is not None
    assert obj.updated_at is not None
```

- [ ] **Step 8.5: Run tests (should fail)**

```bash
DATABASE_URL='mysql://sicoga_user:sicoga_pass@127.0.0.1:3306/sicoga_test' \
  pytest apps/core/tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: apps.core.models`.

- [ ] **Step 8.6: Implement `apps/core/models.py`**

```python
"""Abstract base models for SiCoGa."""
from django.db import models


class TimeStampedModel(models.Model):
    """Adds created_at / updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        abstract = True


class AuditableModel(TimeStampedModel):
    """Adds soft-delete via `activo`. Combine with HistoricalRecords() in concrete models."""

    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        abstract = True
```

- [ ] **Step 8.7: Run tests (should pass)**

```bash
DATABASE_URL='mysql://sicoga_user:sicoga_pass@127.0.0.1:3306/sicoga_test' \
  pytest apps/core/tests/test_models.py -v
```

Expected: 3 PASS.

- [ ] **Step 8.8: Create `apps/core/mixins.py`**

```python
"""View mixins shared across catalog apps."""
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class CatalogoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Login + permission required. Returns 403 (raise_exception) instead of redirect."""

    raise_exception = True
    paginate_by = 25
```

- [ ] **Step 8.9: Commit**

```bash
git add apps/core/ config/settings/base.py
git commit -m "feat(core): add abstract models and catalog mixin"
```

---

## Phase 3 — Accounts (Tasks 9–13)

### Task 9: Custom User model

**Files:**
- Create: `apps/accounts/__init__.py`
- Create: `apps/accounts/apps.py`
- Create: `apps/accounts/models.py`
- Create: `apps/accounts/admin.py`
- Create: `apps/accounts/tests/__init__.py`
- Create: `apps/accounts/tests/test_models.py`
- Modify: `config/settings/base.py` (`AUTH_USER_MODEL`, register app)
- Create: `apps/accounts/migrations/__init__.py`

**⚠️ CRITICAL:** El modelo `User` custom **debe crearse antes** de la primera migración del proyecto. Si ya corriste `migrate`, hay que tirar la BD y volver a empezar:

```bash
mysql -u root -p -e "DROP DATABASE sicoga_dev; DROP DATABASE sicoga_test; CREATE DATABASE sicoga_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE DATABASE sicoga_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; GRANT ALL ON sicoga_dev.* TO 'sicoga_user'@'localhost'; GRANT ALL ON sicoga_test.* TO 'sicoga_user'@'localhost'; FLUSH PRIVILEGES;"
```

**Steps:**

- [ ] **Step 9.1: Create app skeleton**

```bash
mkdir -p apps/accounts/tests apps/accounts/migrations
touch apps/accounts/__init__.py
touch apps/accounts/tests/__init__.py
touch apps/accounts/migrations/__init__.py
```

- [ ] **Step 9.2: Create `apps/accounts/apps.py`**

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Cuentas"
```

- [ ] **Step 9.3: Register in `INSTALLED_APPS` and set `AUTH_USER_MODEL`**

Edit `config/settings/base.py`. After `"apps.core",`:

```python
    "apps.accounts",
```

At the end of the file:

```python
AUTH_USER_MODEL = "accounts.User"
```

- [ ] **Step 9.4: Write failing test**

`apps/accounts/tests/test_models.py`:

```python
"""Tests for User and Profile models."""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


def test_user_email_must_be_unique():
    User.objects.create_user(username="a", email="x@example.com", password="p")
    with pytest.raises(Exception):
        User.objects.create_user(username="b", email="x@example.com", password="p")


def test_user_can_have_telefono():
    u = User.objects.create_user(username="a", email="a@x.com", password="p", telefono="555-123")
    assert u.telefono == "555-123"


def test_user_str_returns_username():
    u = User.objects.create_user(username="anita", email="a@x.com", password="p")
    assert str(u) == "anita"
```

- [ ] **Step 9.5: Run tests (fail)**

```bash
DATABASE_URL='mysql://sicoga_user:sicoga_pass@127.0.0.1:3306/sicoga_test' \
  pytest apps/accounts/tests/test_models.py -v
```

Expected: FAIL — modelo no existe.

- [ ] **Step 9.6: Implement `apps/accounts/models.py`**

```python
"""User and Profile models."""
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class User(AbstractUser):
    """Custom user with unique email and phone field."""

    email = models.EmailField(unique=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username


class Profile(TimeStampedModel):
    """Per-user profile with optional avatar and job title."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    puesto = models.CharField(max_length=80, blank=True, verbose_name="Puesto")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Avatar")

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"Perfil de {self.user.username}"
```

- [ ] **Step 9.7: Generate migration**

```bash
python manage.py makemigrations accounts
```

Expected: `Migrations for 'accounts': accounts/migrations/0001_initial.py - Create model User - Create model Profile`.

- [ ] **Step 9.8: Run migrate**

```bash
python manage.py migrate
```

Expected: aplica `accounts.0001_initial` y todas las anteriores.

- [ ] **Step 9.9: Run tests (pass)**

```bash
pytest apps/accounts/tests/test_models.py -v
```

Expected: 3 PASS.

- [ ] **Step 9.10: Register in admin**

`apps/accounts/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Extras", {"fields": ("telefono",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Extras", {"fields": ("telefono",)}),)
    list_display = ("username", "email", "first_name", "last_name", "telefono", "is_staff")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "puesto", "created_at")
    search_fields = ("user__username", "user__email", "puesto")
```

- [ ] **Step 9.11: Commit**

```bash
git add apps/accounts/ config/settings/base.py
git commit -m "feat(accounts): add custom User model with email unique and Profile"
```

---

### Task 10: Profile auto-creation signal

**Files:**
- Create: `apps/accounts/signals.py`
- Modify: `apps/accounts/apps.py` (register signals)
- Create: `apps/accounts/tests/test_signals.py`

**Steps:**

- [ ] **Step 10.1: Write failing test**

`apps/accounts/tests/test_signals.py`:

```python
"""Tests for accounts signals."""
import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Profile

User = get_user_model()


def test_profile_created_automatically_on_user_create():
    u = User.objects.create_user(username="auto", email="a@x.com", password="p")
    assert Profile.objects.filter(user=u).exists()


def test_profile_not_recreated_on_save():
    u = User.objects.create_user(username="once", email="o@x.com", password="p")
    u.first_name = "Cambio"
    u.save()
    assert Profile.objects.filter(user=u).count() == 1
```

- [ ] **Step 10.2: Run tests (fail)**

```bash
pytest apps/accounts/tests/test_signals.py -v
```

Expected: FAIL — no se crea el Profile.

- [ ] **Step 10.3: Create signal**

`apps/accounts/signals.py`:

```python
"""Signals for the accounts app."""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

- [ ] **Step 10.4: Wire signals in `apps/accounts/apps.py`**

Replace contents:

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Cuentas"

    def ready(self):
        from . import signals  # noqa: F401
```

- [ ] **Step 10.5: Run tests (pass)**

```bash
pytest apps/accounts/tests/test_signals.py -v
```

Expected: 2 PASS.

- [ ] **Step 10.6: Commit**

```bash
git add apps/accounts/signals.py apps/accounts/apps.py apps/accounts/tests/test_signals.py
git commit -m "feat(accounts): auto-create Profile on user creation via signal"
```

---

### Task 11: Auth views (login/logout/password change) and URLs

**Files:**
- Create: `apps/accounts/urls.py`
- Modify: `config/urls.py`
- Create: `apps/accounts/tests/test_views.py`

**Steps:**

- [ ] **Step 11.1: Create `apps/accounts/urls.py`**

```python
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url="/accounts/password/change/done/",
        ),
        name="password_change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("perfil/", views.ProfileView.as_view(), name="perfil"),
]
```

- [ ] **Step 11.2: Create `apps/accounts/views.py`**

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ProfileForm
from .models import Profile


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/perfil.html"
    success_url = reverse_lazy("accounts:perfil")

    def get_object(self, queryset=None):
        return self.request.user.profile
```

- [ ] **Step 11.3: Create `apps/accounts/forms.py`**

```python
from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["puesto", "avatar"]
        widgets = {
            "puesto": forms.TextInput(attrs={"class": "input"}),
        }
```

- [ ] **Step 11.4: Wire `apps/accounts/urls.py` into `config/urls.py`**

Replace `config/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path(
        "",
        TemplateView.as_view(template_name="dashboard/home.html"),
        name="dashboard-home-stub",
    ),
]
```

- [ ] **Step 11.5: Write tests for auth flow**

`apps/accounts/tests/test_views.py`:

```python
"""Tests for accounts views."""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(username="ana", email="a@x.com", password="pass1234!")


def test_login_url_resolves(client):
    response = client.get(reverse("accounts:login"))
    assert response.status_code == 200


def test_login_with_valid_credentials(client, user):
    response = client.post(
        reverse("accounts:login"),
        {"username": "ana", "password": "pass1234!"},
        follow=False,
    )
    assert response.status_code == 302


def test_login_with_invalid_credentials_shows_error(client, user):
    response = client.post(
        reverse("accounts:login"),
        {"username": "ana", "password": "wrong"},
    )
    assert response.status_code == 200
    assert b"correctos" in response.content or b"correcta" in response.content or b"v" in response.content


def test_perfil_requires_login(client):
    response = client.get(reverse("accounts:perfil"))
    assert response.status_code == 302
    assert "/accounts/login/" in response.url


def test_perfil_accessible_when_logged_in(client, user):
    client.force_login(user)
    response = client.get(reverse("accounts:perfil"))
    assert response.status_code == 200
```

- [ ] **Step 11.6: Run tests — expected 4/5 to pass (login template missing)**

```bash
pytest apps/accounts/tests/test_views.py -v
```

> Templates se crean en Task 15. Por ahora el test del template puede fallar; lo arreglamos al crear `templates/accounts/login.html`.

- [ ] **Step 11.7: Commit**

```bash
git add apps/accounts/urls.py apps/accounts/views.py apps/accounts/forms.py config/urls.py apps/accounts/tests/test_views.py
git commit -m "feat(accounts): add login/logout/password and profile views"
```

---

### Task 12: Data migration — seed 4 groups with permissions

**Files:**
- Create: `apps/accounts/migrations/0002_seed_groups.py`
- Create: `apps/accounts/tests/test_seed_groups.py`

**Steps:**

- [ ] **Step 12.1: Write failing test**

`apps/accounts/tests/test_seed_groups.py`:

```python
"""Tests for the seeded groups."""
import pytest
from django.contrib.auth.models import Group


@pytest.mark.django_db
def test_four_groups_exist():
    expected = {"Administrador", "Gerente", "Capturista", "Solo Lectura"}
    actual = set(Group.objects.values_list("name", flat=True))
    assert expected.issubset(actual)


@pytest.mark.django_db
def test_solo_lectura_has_only_view_permissions():
    g = Group.objects.get(name="Solo Lectura")
    perms = g.permissions.values_list("codename", flat=True)
    assert all(p.startswith("view_") for p in perms)


@pytest.mark.django_db
def test_administrador_has_all_permissions():
    from django.contrib.auth.models import Permission

    g = Group.objects.get(name="Administrador")
    assert g.permissions.count() == Permission.objects.count()
```

- [ ] **Step 12.2: Run tests (fail)**

```bash
pytest apps/accounts/tests/test_seed_groups.py -v
```

Expected: FAIL — grupos no existen.

- [ ] **Step 12.3: Create data migration**

`apps/accounts/migrations/0002_seed_groups.py`:

```python
"""Seed the four standard groups with their permissions."""
from django.db import migrations


GROUP_DEFINITIONS = {
    "Administrador": "ALL",
    "Gerente": ["view"],
    "Capturista": ["view"],
    "Solo Lectura": ["view"],
}


def seed_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for name, scope in GROUP_DEFINITIONS.items():
        group, _ = Group.objects.get_or_create(name=name)
        if scope == "ALL":
            group.permissions.set(Permission.objects.all())
        else:
            perms = Permission.objects.filter(
                codename__regex=r"^(" + "|".join(scope) + r")_"
            )
            group.permissions.set(perms)


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=GROUP_DEFINITIONS.keys()).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(seed_groups, remove_groups),
    ]
```

- [ ] **Step 12.4: Apply migration**

```bash
python manage.py migrate accounts
```

Expected: `Applying accounts.0002_seed_groups... OK`.

- [ ] **Step 12.5: Run tests (pass)**

```bash
pytest apps/accounts/tests/test_seed_groups.py -v
```

Expected: 3 PASS.

- [ ] **Step 12.6: Commit**

```bash
git add apps/accounts/migrations/0002_seed_groups.py apps/accounts/tests/test_seed_groups.py
git commit -m "feat(accounts): seed four standard user groups via data migration"
```

---

### Task 13: Wire `LOGIN_URL` and verify with end-to-end smoke

**Files:**
- Modify: `config/settings/base.py` (already has LOGIN_URL — verificar)

**Steps:**

- [ ] **Step 13.1: Verify settings**

```bash
grep -n "LOGIN_URL\|LOGIN_REDIRECT_URL\|LOGOUT_REDIRECT_URL" config/settings/base.py
```

Expected: las tres líneas presentes (definidas en Task 3).

- [ ] **Step 13.2: Commit (no-op si ya estaba)**

No requiere commit si los valores ya están en `base.py` desde Task 3.

---

## Phase 4 — Static + base templates (Tasks 14–17)

### Task 14: Port CSS from dummy v4 to `static/`

**Files:**
- Create: `static/css/sicoga.css`
- Create: `static/js/sicoga.js`

**Steps:**

- [ ] **Step 14.1: Create static dirs**

```bash
mkdir -p static/css static/js static/img
```

- [ ] **Step 14.2: Extract `<style>` block from dummy**

```bash
python3 - <<'PY'
import re
src = open('docs/SistemaGanadero_Demo_v4.html').read()
style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
open('static/css/sicoga.css', 'w').write(style.strip() + '\n')
print(f"Wrote {len(style)} chars to static/css/sicoga.css")
PY
```

Expected: archivo CSS creado con ~1000+ líneas.

- [ ] **Step 14.3: Extract `<script>` JS body (excluir templates de pantallas)**

```bash
python3 - <<'PY'
import re
src = open('docs/SistemaGanadero_Demo_v4.html').read()
scripts = re.findall(r'<script>(.*?)</script>', src, re.S)
nav_js = scripts[0] if scripts else ''
open('static/js/sicoga.js', 'w').write(nav_js.strip() + '\n')
print(f"Wrote {len(nav_js)} chars to static/js/sicoga.js")
PY
```

> Nota: el JS del dummy maneja la navegación entre "pantallas" como divs ocultos. En el sistema Django real, cada pantalla es una URL separada, así que este JS se irá adaptando. Por ahora lo guardamos como referencia.

- [ ] **Step 14.4: Commit**

```bash
git add static/
git commit -m "feat: port css and js from dummy v4 prototype"
```

---

### Task 15: Create `base.html` and partials

**Files:**
- Create: `templates/base.html`
- Create: `templates/partials/_header.html`
- Create: `templates/partials/_sidebar.html`
- Create: `templates/partials/_flashes.html`
- Create: `templates/partials/_pagination.html`
- Create: `templates/partials/_delete_confirm.html`
- Create: `templates/accounts/login.html`
- Create: `templates/accounts/perfil.html`
- Create: `templates/accounts/password_change.html`
- Create: `templates/accounts/password_change_done.html`

**Steps:**

- [ ] **Step 15.1: Create dirs**

```bash
mkdir -p templates/partials templates/accounts templates/dashboard templates/catalogos
```

- [ ] **Step 15.2: Create `templates/base.html`**

```html
{% load static %}<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}SiCoGa{% endblock %} — SIWEB</title>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/sicoga.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  {% include "partials/_header.html" %}
  <div class="layout">
    {% include "partials/_sidebar.html" %}
    <main>
      {% include "partials/_flashes.html" %}
      {% block content %}{% endblock %}
    </main>
  </div>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <script defer src="https://unpkg.com/alpinejs@3.14.1/dist/cdn.min.js"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

- [ ] **Step 15.3: Create `_header.html`**

```html
{% load static %}
<header>
  <div class="logo">SiCoGa <span>SIWEB</span></div>
  <div class="sem">Semana actual: {% now "W" %} / {% now "Y" %}</div>
  <div class="hdr-r">
    {% if user.is_authenticated %}
      <span style="font-size:12px;color:var(--txd);">{{ user.username }}</span>
      <a href="{% url 'accounts:perfil' %}" class="avatar">{{ user.username|slice:":1"|upper }}</a>
      <form method="post" action="{% url 'accounts:logout' %}" style="display:inline;">
        {% csrf_token %}
        <button type="submit" class="btn bo bsm">Salir</button>
      </form>
    {% else %}
      <a href="{% url 'accounts:login' %}" class="btn bp bsm">Entrar</a>
    {% endif %}
  </div>
</header>
```

- [ ] **Step 15.4: Create `_sidebar.html`**

```html
<aside>
  <div class="nsec">Dashboard</div>
  <a class="ni {% if request.resolver_match.url_name == 'dashboard-home-stub' %}active{% endif %}" href="/">
    <span class="ico">▦</span> Inicio
  </a>

  <div class="ndiv"></div>
  <div class="nsec">Catálogos</div>
  <a class="ni {% if 'corral' in request.path and 'tipo' not in request.path %}active{% endif %}" href="{% url 'catalogos:corral_list' %}">
    <span class="ico">▢</span> Corrales
  </a>
  <a class="ni {% if 'tipos-corral' in request.path %}active{% endif %}" href="{% url 'catalogos:tipocorral_list' %}">
    <span class="ico">▢</span> Tipos de Corral
  </a>
  <a class="ni {% if 'tipos-ganado' in request.path %}active{% endif %}" href="{% url 'catalogos:tipoganado_list' %}">
    <span class="ico">▢</span> Tipos de Ganado
  </a>
  <a class="ni {% if 'tipos-origen' in request.path %}active{% endif %}" href="{% url 'catalogos:tipoorigen_list' %}">
    <span class="ico">▢</span> Tipos de Origen
  </a>
  <a class="ni {% if 'proveedores' in request.path %}active{% endif %}" href="{% url 'catalogos:proveedor_list' %}">
    <span class="ico">▢</span> Proveedores
  </a>
  <a class="ni {% if 'programa-reimplantes' in request.path %}active{% endif %}" href="{% url 'catalogos:programareimplante_list' %}">
    <span class="ico">▢</span> Programa de Reimplantes
  </a>

  <div class="ndiv"></div>
  <div class="nsec">Próximamente</div>
  <a class="ni" style="opacity:.4;cursor:not-allowed;"><span class="ico">▢</span> Disponibilidad <span class="nbg d">soon</span></a>
  <a class="ni" style="opacity:.4;cursor:not-allowed;"><span class="ico">▢</span> Cierre de Lotes <span class="nbg d">soon</span></a>
  <a class="ni" style="opacity:.4;cursor:not-allowed;"><span class="ico">▢</span> Reportes <span class="nbg d">soon</span></a>

  {% if user.is_staff %}
    <div class="ndiv"></div>
    <div class="nsec">Administración</div>
    <a class="ni" href="/admin/"><span class="ico">⚙</span> Admin Django</a>
  {% endif %}
</aside>
```

- [ ] **Step 15.5: Create `_flashes.html`**

```html
{% if messages %}
<div class="ali" style="margin-bottom:18px;">
  {% for msg in messages %}
    <div class="ai {% if msg.tags == 'success' %}ok{% elif msg.tags == 'warning' %}warn{% elif msg.tags == 'error' %}err{% else %}info{% endif %}">
      {{ msg }}
    </div>
  {% endfor %}
</div>
{% endif %}
```

- [ ] **Step 15.6: Create `_pagination.html`**

```html
{% if is_paginated %}
<nav class="bg" style="margin-top:14px;justify-content:center;">
  {% if page_obj.has_previous %}
    <a class="btn bo bsm" href="?page={{ page_obj.previous_page_number }}">‹ Anterior</a>
  {% endif %}
  <span style="font-size:12px;color:var(--txd);padding:0 10px;">
    Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}
  </span>
  {% if page_obj.has_next %}
    <a class="btn bo bsm" href="?page={{ page_obj.next_page_number }}">Siguiente ›</a>
  {% endif %}
</nav>
{% endif %}
```

- [ ] **Step 15.7: Create `_delete_confirm.html`**

```html
{% extends "base.html" %}
{% block content %}
<div class="ph"><div><div class="ptitle">Eliminar registro</div><div class="psub">Esta acción se puede revertir desde el admin.</div></div></div>
<div class="card">
  <p style="margin-bottom:14px;">¿Eliminar <strong>{{ object }}</strong>?</p>
  <form method="post">
    {% csrf_token %}
    <button type="submit" class="btn ba">Sí, eliminar</button>
    <a href="{{ cancel_url|default:'../' }}" class="btn bo">Cancelar</a>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 15.8: Create `templates/accounts/login.html`**

```html
{% extends "base.html" %}
{% block title %}Iniciar sesión{% endblock %}
{% block content %}
<div class="ph"><div><div class="ptitle">Iniciar sesión</div></div></div>
<div class="card" style="max-width:360px;">
  <form method="post">
    {% csrf_token %}
    {% if form.non_field_errors %}
      <div class="ai err" style="margin-bottom:10px;">{{ form.non_field_errors }}</div>
    {% endif %}
    <div style="margin-bottom:12px;">
      <label class="klbl">Usuario</label>
      <input class="input" type="text" name="username" required style="width:100%;padding:8px;">
    </div>
    <div style="margin-bottom:12px;">
      <label class="klbl">Contraseña</label>
      <input class="input" type="password" name="password" required style="width:100%;padding:8px;">
    </div>
    <button type="submit" class="btn bp">Entrar</button>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 15.9: Create `templates/accounts/perfil.html`**

```html
{% extends "base.html" %}
{% block title %}Mi perfil{% endblock %}
{% block content %}
<div class="ph"><div><div class="ptitle">Mi perfil</div><div class="psub">Información personal y avatar</div></div></div>
<div class="card" style="max-width:480px;">
  <p><strong>Usuario:</strong> {{ user.username }}</p>
  <p><strong>Email:</strong> {{ user.email }}</p>
  <p><strong>Teléfono:</strong> {{ user.telefono|default:"—" }}</p>
  <hr style="border:none;border-top:1px solid var(--bdr);margin:14px 0;">
  <form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn bp">Guardar</button>
    <a href="{% url 'accounts:password_change' %}" class="btn bo">Cambiar contraseña</a>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 15.10: Create `templates/accounts/password_change.html` and `_done.html`**

```html
{# password_change.html #}
{% extends "base.html" %}
{% block content %}
<div class="ph"><div class="ptitle">Cambiar contraseña</div></div>
<div class="card" style="max-width:480px;">
  <form method="post">{% csrf_token %}{{ form.as_p }}<button type="submit" class="btn bp">Cambiar</button></form>
</div>
{% endblock %}
```

```html
{# password_change_done.html #}
{% extends "base.html" %}
{% block content %}
<div class="ai ok">Contraseña actualizada correctamente.</div>
<a href="{% url 'accounts:perfil' %}" class="btn bo">Volver al perfil</a>
{% endblock %}
```

- [ ] **Step 15.11: Re-run accounts view tests**

```bash
pytest apps/accounts/tests/test_views.py -v
```

Expected: 5 PASS (incluyendo el de login template).

- [ ] **Step 15.12: Commit**

```bash
git add templates/
git commit -m "feat: add base layout, partials and accounts templates"
```

---

### Task 16: Error pages (400/403/404/500)

**Files:**
- Create: `templates/400.html`, `403.html`, `404.html`, `500.html`

**Steps:**

- [ ] **Step 16.1: Create `templates/404.html`**

```html
{% extends "base.html" %}
{% block title %}Página no encontrada{% endblock %}
{% block content %}
<div class="ph"><div class="ptitle">404 — Página no encontrada</div></div>
<div class="ai err">La página que buscas no existe.</div>
<a href="/" class="btn bp">Ir al inicio</a>
{% endblock %}
```

- [ ] **Step 16.2: Create `403.html`** (analogous, mensaje "No tienes permiso para esta acción.")

```html
{% extends "base.html" %}
{% block title %}Sin permiso{% endblock %}
{% block content %}
<div class="ph"><div class="ptitle">403 — Sin permiso</div></div>
<div class="ai err">No tienes permiso para realizar esta acción.</div>
<a href="/" class="btn bp">Ir al inicio</a>
{% endblock %}
```

- [ ] **Step 16.3: Create `400.html` and `500.html` (mismo patrón)**

```html
{# 400.html #}
{% extends "base.html" %}
{% block content %}
<div class="ph"><div class="ptitle">400 — Solicitud inválida</div></div>
<div class="ai err">Los datos enviados no son válidos.</div>
<a href="/" class="btn bp">Ir al inicio</a>
{% endblock %}
```

```html
{# 500.html — NO usa base.html porque puede fallar; debe ser self-contained #}
{% load static %}
<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Error del servidor</title>
<link rel="stylesheet" href="{% static 'css/sicoga.css' %}"></head>
<body><main style="padding:40px;">
<h1>500 — Error del servidor</h1>
<p>Ocurrió un error inesperado. El equipo técnico fue notificado.</p>
<a href="/" class="btn bp">Ir al inicio</a>
</main></body></html>
```

- [ ] **Step 16.4: Commit**

```bash
git add templates/400.html templates/403.html templates/404.html templates/500.html
git commit -m "feat: add styled error pages 400/403/404/500"
```

---

### Task 17: Dashboard placeholder

**Files:**
- Create: `templates/dashboard/home.html`

**Steps:**

- [ ] **Step 17.1: Create placeholder template**

```html
{% extends "base.html" %}
{% block title %}Bienvenido{% endblock %}
{% block content %}
<div class="ph">
  <div>
    <div class="ptitle">Bienvenido a SiCoGa</div>
    <div class="psub">Sistema Integral de Gestión Ganadera</div>
  </div>
</div>
<div class="card">
  <p>Sistema en desarrollo. Por ahora puedes administrar los siguientes catálogos desde el menú lateral:</p>
  <ul style="margin-top:10px;line-height:1.8;">
    <li>Corrales · Tipos de Corral · Tipos de Ganado · Tipos de Origen</li>
    <li>Proveedores</li>
    <li>Programa de Reimplantes</li>
  </ul>
  <p style="margin-top:14px;color:var(--txd);font-size:12px;">
    Los módulos de Disponibilidad, Cierre y Dashboard ejecutivo se habilitarán en entregables siguientes.
  </p>
</div>
{% endblock %}
```

- [ ] **Step 17.2: Smoke test runserver**

```bash
python manage.py runserver
```

Visitar `/` (sidebar visible, dashboard placeholder), `/accounts/login/`, `/admin/`.

- [ ] **Step 17.3: Commit**

```bash
git add templates/dashboard/home.html
git commit -m "feat: add dashboard placeholder template"
```

---

## Phase 5 — Catálogos simples (Tasks 18–22)

### Task 18: Bootstrap `catalogos` app and URL routing

**Files:**
- Create: `apps/catalogos/__init__.py`
- Create: `apps/catalogos/apps.py`
- Create: `apps/catalogos/urls.py`
- Create: `apps/catalogos/models.py` (vacío inicial)
- Create: `apps/catalogos/admin.py` (vacío inicial)
- Create: `apps/catalogos/views.py` (vacío inicial)
- Create: `apps/catalogos/forms.py` (vacío inicial)
- Create: `apps/catalogos/migrations/__init__.py`
- Create: `apps/catalogos/tests/__init__.py`
- Modify: `config/settings/base.py` (registrar app)
- Modify: `config/urls.py` (incluir urls)

**Steps:**

- [ ] **Step 18.1: Create app skeleton**

```bash
mkdir -p apps/catalogos/migrations apps/catalogos/tests
touch apps/catalogos/__init__.py
touch apps/catalogos/migrations/__init__.py
touch apps/catalogos/tests/__init__.py
touch apps/catalogos/models.py
touch apps/catalogos/admin.py
touch apps/catalogos/views.py
touch apps/catalogos/forms.py
```

- [ ] **Step 18.2: Create `apps/catalogos/apps.py`**

```python
from django.apps import AppConfig


class CatalogosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalogos"
    label = "catalogos"
    verbose_name = "Catálogos"
```

- [ ] **Step 18.3: Register app**

Edit `config/settings/base.py` INSTALLED_APPS, after `"apps.accounts",`:

```python
    "apps.catalogos",
```

- [ ] **Step 18.4: Create `apps/catalogos/urls.py` skeleton**

```python
from django.urls import path

app_name = "catalogos"

urlpatterns = [
    # Se irán añadiendo conforme cada modelo se implemente.
]
```

- [ ] **Step 18.5: Wire into `config/urls.py`**

Edit `config/urls.py`, add inside `urlpatterns`:

```python
    path("catalogos/", include("apps.catalogos.urls", namespace="catalogos")),
```

- [ ] **Step 18.6: Verify**

```bash
python manage.py check
```

Expected: `System check identified no issues`.

- [ ] **Step 18.7: Commit**

```bash
git add apps/catalogos/ config/settings/base.py config/urls.py
git commit -m "feat(catalogos): bootstrap empty app with URL routing"
```

---

### Task 19: TipoCorral CRUD

**Files:**
- Modify: `apps/catalogos/models.py`
- Modify: `apps/catalogos/admin.py`
- Modify: `apps/catalogos/forms.py`
- Modify: `apps/catalogos/views.py`
- Modify: `apps/catalogos/urls.py`
- Create: `templates/catalogos/_form.html`
- Create: `templates/catalogos/tipocorral_list.html`
- Create: `templates/catalogos/tipocorral_form.html`
- Create: `templates/catalogos/tipocorral_detail.html`
- Create: `templates/catalogos/tipocorral_confirm_delete.html`
- Create: `apps/catalogos/tests/test_tipocorral.py`

**Steps:**

- [ ] **Step 19.1: Write failing model test**

`apps/catalogos/tests/test_tipocorral.py`:

```python
"""Tests for TipoCorral CRUD and behavior."""
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def admin_user():
    u = User.objects.create_user(username="admin", email="a@x.com", password="p", is_staff=True)
    u.groups.add(Group.objects.get(name="Administrador"))
    return u


@pytest.fixture
def lectura_user():
    u = User.objects.create_user(username="lectura", email="l@x.com", password="p")
    u.groups.add(Group.objects.get(name="Solo Lectura"))
    return u


@pytest.mark.django_db
def test_tipocorral_str_returns_nombre():
    from apps.catalogos.models import TipoCorral

    t = TipoCorral.objects.create(nombre="Recepción")
    assert str(t) == "Recepción"


@pytest.mark.django_db
def test_tipocorral_nombre_unique():
    from apps.catalogos.models import TipoCorral

    TipoCorral.objects.create(nombre="Engorda")
    with pytest.raises(Exception):
        TipoCorral.objects.create(nombre="Engorda")


@pytest.mark.django_db
def test_tipocorral_history_records_changes():
    from apps.catalogos.models import TipoCorral

    t = TipoCorral.objects.create(nombre="X")
    t.nombre = "Y"
    t.save()
    assert t.history.count() == 2


def test_tipocorral_list_requires_login(client):
    response = client.get(reverse("catalogos:tipocorral_list"))
    assert response.status_code == 302


def test_admin_can_access_list(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse("catalogos:tipocorral_list"))
    assert response.status_code == 200


def test_lectura_can_view_but_not_create(client, lectura_user):
    client.force_login(lectura_user)
    assert client.get(reverse("catalogos:tipocorral_list")).status_code == 200
    assert client.get(reverse("catalogos:tipocorral_create")).status_code == 403


def test_admin_can_create_tipocorral(client, admin_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("catalogos:tipocorral_create"),
        {"nombre": "Zilpaterol", "activo": "on"},
        follow=True,
    )
    assert response.status_code == 200
    from apps.catalogos.models import TipoCorral

    assert TipoCorral.objects.filter(nombre="Zilpaterol").exists()


def test_soft_delete_sets_activo_false(client, admin_user):
    from apps.catalogos.models import TipoCorral

    t = TipoCorral.objects.create(nombre="Tmp")
    client.force_login(admin_user)
    client.post(reverse("catalogos:tipocorral_delete", args=[t.pk]))
    t.refresh_from_db()
    assert t.activo is False
```

- [ ] **Step 19.2: Run tests (fail)**

```bash
pytest apps/catalogos/tests/test_tipocorral.py -v
```

Expected: FAIL — modelo y vistas no existen.

- [ ] **Step 19.3: Implement model in `apps/catalogos/models.py`**

```python
"""Catálogos de SiCoGa."""
from simple_history.models import HistoricalRecords

from django.db import models

from apps.core.models import AuditableModel


class TipoCorral(AuditableModel):
    nombre = models.CharField(max_length=40, unique=True, verbose_name="Nombre")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Tipo de corral"
        verbose_name_plural = "Tipos de corral"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
```

- [ ] **Step 19.4: Make migration**

```bash
python manage.py makemigrations catalogos
python manage.py migrate
```

- [ ] **Step 19.5: Register admin**

Edit `apps/catalogos/admin.py`:

```python
from simple_history.admin import SimpleHistoryAdmin

from django.contrib import admin

from .models import TipoCorral


@admin.register(TipoCorral)
class TipoCorralAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "activo", "updated_at")
    list_filter = ("activo",)
    search_fields = ("nombre",)
```

- [ ] **Step 19.6: Form**

Edit `apps/catalogos/forms.py`:

```python
from django import forms

from .models import TipoCorral


class TipoCorralForm(forms.ModelForm):
    class Meta:
        model = TipoCorral
        fields = ["nombre", "activo"]
        widgets = {"nombre": forms.TextInput(attrs={"class": "input", "autofocus": True})}
```

- [ ] **Step 19.7: Views**

Edit `apps/catalogos/views.py`:

```python
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django.shortcuts import get_object_or_404

from apps.core.mixins import CatalogoMixin

from .forms import TipoCorralForm
from .models import TipoCorral


# ----- TipoCorral -----
class TipoCorralListView(CatalogoMixin, ListView):
    model = TipoCorral
    template_name = "catalogos/tipocorral_list.html"
    permission_required = "catalogos.view_tipocorral"
    context_object_name = "objetos"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs


class TipoCorralCreateView(CatalogoMixin, CreateView):
    model = TipoCorral
    form_class = TipoCorralForm
    template_name = "catalogos/tipocorral_form.html"
    permission_required = "catalogos.add_tipocorral"
    success_url = reverse_lazy("catalogos:tipocorral_list")


class TipoCorralUpdateView(CatalogoMixin, UpdateView):
    model = TipoCorral
    form_class = TipoCorralForm
    template_name = "catalogos/tipocorral_form.html"
    permission_required = "catalogos.change_tipocorral"
    success_url = reverse_lazy("catalogos:tipocorral_list")


class TipoCorralDetailView(CatalogoMixin, DetailView):
    model = TipoCorral
    template_name = "catalogos/tipocorral_detail.html"
    permission_required = "catalogos.view_tipocorral"
    context_object_name = "obj"


class TipoCorralDeleteView(CatalogoMixin, View):
    permission_required = "catalogos.delete_tipocorral"

    def get(self, request, pk):
        obj = get_object_or_404(TipoCorral, pk=pk)
        return self._render_confirm(request, obj)

    def post(self, request, pk):
        obj = get_object_or_404(TipoCorral, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("catalogos:tipocorral_list")

    def _render_confirm(self, request, obj):
        from django.shortcuts import render

        return render(
            request,
            "catalogos/tipocorral_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("catalogos:tipocorral_list")},
        )
```

- [ ] **Step 19.8: Wire URLs in `apps/catalogos/urls.py`**

```python
from django.urls import path

from . import views

app_name = "catalogos"

urlpatterns = [
    # TipoCorral
    path("tipos-corral/", views.TipoCorralListView.as_view(), name="tipocorral_list"),
    path("tipos-corral/nuevo/", views.TipoCorralCreateView.as_view(), name="tipocorral_create"),
    path("tipos-corral/<int:pk>/", views.TipoCorralDetailView.as_view(), name="tipocorral_detail"),
    path("tipos-corral/<int:pk>/editar/", views.TipoCorralUpdateView.as_view(), name="tipocorral_update"),
    path("tipos-corral/<int:pk>/eliminar/", views.TipoCorralDeleteView.as_view(), name="tipocorral_delete"),
]
```

- [ ] **Step 19.9: Create templates**

`templates/catalogos/_form.html`:

```html
<form method="post">
  {% csrf_token %}
  {% for field in form %}
    <div style="margin-bottom:12px;">
      <label class="klbl">{{ field.label }}</label>
      {{ field }}
      {% if field.errors %}<div class="ai err">{{ field.errors|join:", " }}</div>{% endif %}
      {% if field.help_text %}<div class="psub">{{ field.help_text }}</div>{% endif %}
    </div>
  {% endfor %}
  <button type="submit" class="btn bp">Guardar</button>
  <a href="{{ cancel_url }}" class="btn bo">Cancelar</a>
</form>
```

`templates/catalogos/tipocorral_list.html`:

```html
{% extends "base.html" %}
{% block title %}Tipos de Corral{% endblock %}
{% block content %}
<div class="ph">
  <div><div class="ptitle">Tipos de Corral</div><div class="psub">Categorías de los corrales del rancho</div></div>
  <div class="bg">
    {% if perms.catalogos.add_tipocorral %}
      <a href="{% url 'catalogos:tipocorral_create' %}" class="btn bp">+ Nuevo</a>
    {% endif %}
  </div>
</div>
<div class="card">
  <table class="tbl">
    <thead><tr><th>Nombre</th><th>Estado</th><th>Actualizado</th><th></th></tr></thead>
    <tbody>
      {% for o in objetos %}
        <tr>
          <td>{{ o.nombre }}</td>
          <td><span class="pill {% if o.activo %}pg{% else %}pr{% endif %}">{% if o.activo %}Activo{% else %}Inactivo{% endif %}</span></td>
          <td class="mn">{{ o.updated_at|date:"Y-m-d H:i" }}</td>
          <td>
            {% if perms.catalogos.change_tipocorral %}
              <a href="{% url 'catalogos:tipocorral_update' o.pk %}" class="btn bo bsm">Editar</a>
            {% endif %}
            {% if perms.catalogos.delete_tipocorral and o.activo %}
              <a href="{% url 'catalogos:tipocorral_delete' o.pk %}" class="btn bo bsm">Eliminar</a>
            {% endif %}
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="4" style="color:var(--txd);text-align:center;">Sin registros.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% include "partials/_pagination.html" %}
{% endblock %}
```

`templates/catalogos/tipocorral_form.html`:

```html
{% extends "base.html" %}
{% block title %}{% if object %}Editar{% else %}Nuevo{% endif %} Tipo de Corral{% endblock %}
{% block content %}
<div class="ph"><div><div class="ptitle">{% if object %}Editar{% else %}Nuevo{% endif %} Tipo de Corral</div></div></div>
<div class="card" style="max-width:480px;">
  {% include "catalogos/_form.html" with cancel_url=request.META.HTTP_REFERER %}
</div>
{% endblock %}
```

`templates/catalogos/tipocorral_detail.html`:

```html
{% extends "base.html" %}
{% block title %}{{ obj.nombre }}{% endblock %}
{% block content %}
<div class="ph"><div><div class="ptitle">{{ obj.nombre }}</div><div class="psub">Tipo de corral</div></div></div>
<div class="card">
  <p><strong>Estado:</strong> {{ obj.activo|yesno:"Activo,Inactivo" }}</p>
  <p><strong>Creado:</strong> {{ obj.created_at|date:"Y-m-d H:i" }}</p>
  <p><strong>Actualizado:</strong> {{ obj.updated_at|date:"Y-m-d H:i" }}</p>
  <a href="{% url 'catalogos:tipocorral_update' obj.pk %}" class="btn bp">Editar</a>
  <a href="{% url 'catalogos:tipocorral_list' %}" class="btn bo">Volver</a>
</div>
{% endblock %}
```

`templates/catalogos/tipocorral_confirm_delete.html`:

```html
{% extends "partials/_delete_confirm.html" %}
```

- [ ] **Step 19.10: Run tests (pass)**

```bash
pytest apps/catalogos/tests/test_tipocorral.py -v
```

Expected: 8 PASS.

- [ ] **Step 19.11: Commit**

```bash
git add apps/catalogos/ templates/catalogos/
git commit -m "feat(catalogos): add TipoCorral CRUD with history and soft delete"
```

---

### Task 20: TipoGanado CRUD

**Same pattern as Task 19** (model only `nombre + activo + history`, mismo CRUD).

**Files:**
- Modify: `apps/catalogos/models.py` (añadir `TipoGanado`)
- Modify: `apps/catalogos/admin.py`, `forms.py`, `views.py`, `urls.py`
- Create: `templates/catalogos/tipoganado_*.html`
- Create: `apps/catalogos/tests/test_tipoganado.py`

**Steps:**

- [ ] **Step 20.1: Add model to `apps/catalogos/models.py`**

```python
class TipoGanado(AuditableModel):
    nombre = models.CharField(max_length=40, unique=True, verbose_name="Nombre")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Tipo de ganado"
        verbose_name_plural = "Tipos de ganado"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
```

- [ ] **Step 20.2: Migrate**

```bash
python manage.py makemigrations catalogos
python manage.py migrate
```

- [ ] **Step 20.3: Add to admin (after TipoCorral)**

```python
from .models import TipoGanado

@admin.register(TipoGanado)
class TipoGanadoAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "activo", "updated_at")
    list_filter = ("activo",)
    search_fields = ("nombre",)
```

- [ ] **Step 20.4: Add form**

```python
from .models import TipoGanado

class TipoGanadoForm(forms.ModelForm):
    class Meta:
        model = TipoGanado
        fields = ["nombre", "activo"]
        widgets = {"nombre": forms.TextInput(attrs={"class": "input", "autofocus": True})}
```

- [ ] **Step 20.5: Add views (5 vistas siguiendo el mismo patrón que TipoCorral)**

Append to `apps/catalogos/views.py`:

```python
from .forms import TipoGanadoForm
from .models import TipoGanado


class TipoGanadoListView(CatalogoMixin, ListView):
    model = TipoGanado
    template_name = "catalogos/tipoganado_list.html"
    permission_required = "catalogos.view_tipoganado"
    context_object_name = "objetos"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs


class TipoGanadoCreateView(CatalogoMixin, CreateView):
    model = TipoGanado
    form_class = TipoGanadoForm
    template_name = "catalogos/tipoganado_form.html"
    permission_required = "catalogos.add_tipoganado"
    success_url = reverse_lazy("catalogos:tipoganado_list")


class TipoGanadoUpdateView(CatalogoMixin, UpdateView):
    model = TipoGanado
    form_class = TipoGanadoForm
    template_name = "catalogos/tipoganado_form.html"
    permission_required = "catalogos.change_tipoganado"
    success_url = reverse_lazy("catalogos:tipoganado_list")


class TipoGanadoDetailView(CatalogoMixin, DetailView):
    model = TipoGanado
    template_name = "catalogos/tipoganado_detail.html"
    permission_required = "catalogos.view_tipoganado"
    context_object_name = "obj"


class TipoGanadoDeleteView(CatalogoMixin, View):
    permission_required = "catalogos.delete_tipoganado"

    def get(self, request, pk):
        obj = get_object_or_404(TipoGanado, pk=pk)
        from django.shortcuts import render

        return render(
            request,
            "catalogos/tipoganado_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("catalogos:tipoganado_list")},
        )

    def post(self, request, pk):
        obj = get_object_or_404(TipoGanado, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("catalogos:tipoganado_list")
```

- [ ] **Step 20.6: Add URLs**

Append to `apps/catalogos/urls.py`:

```python
    # TipoGanado
    path("tipos-ganado/", views.TipoGanadoListView.as_view(), name="tipoganado_list"),
    path("tipos-ganado/nuevo/", views.TipoGanadoCreateView.as_view(), name="tipoganado_create"),
    path("tipos-ganado/<int:pk>/", views.TipoGanadoDetailView.as_view(), name="tipoganado_detail"),
    path("tipos-ganado/<int:pk>/editar/", views.TipoGanadoUpdateView.as_view(), name="tipoganado_update"),
    path("tipos-ganado/<int:pk>/eliminar/", views.TipoGanadoDeleteView.as_view(), name="tipoganado_delete"),
```

- [ ] **Step 20.7: Create 4 templates copying TipoCorral and replacing strings**

`templates/catalogos/tipoganado_list.html`, `_form.html`, `_detail.html`, `_confirm_delete.html` — mismo patrón que TipoCorral cambiando "TipoCorral" → "TipoGanado", "tipocorral" → "tipoganado", "Tipo de Corral" → "Tipo de Ganado".

- [ ] **Step 20.8: Tests**

`apps/catalogos/tests/test_tipoganado.py` — copia de `test_tipocorral.py` cambiando referencias.

- [ ] **Step 20.9: Run tests**

```bash
pytest apps/catalogos/tests/test_tipoganado.py -v
```

Expected: 8 PASS.

- [ ] **Step 20.10: Commit**

```bash
git add apps/catalogos/ templates/catalogos/tipoganado_*
git commit -m "feat(catalogos): add TipoGanado CRUD"
```

---

### Task 21: TipoOrigen CRUD

**Same pattern as Task 20.** Modelo:

```python
class TipoOrigen(AuditableModel):
    nombre = models.CharField(max_length=20, unique=True, verbose_name="Nombre")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Tipo de origen"
        verbose_name_plural = "Tipos de origen"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
```

URLs prefix: `tipos-origen/`. URL names: `tipoorigen_list`, `tipoorigen_create`, `tipoorigen_detail`, `tipoorigen_update`, `tipoorigen_delete`.

Repetir Steps 20.1–20.10 cambiando `TipoGanado` → `TipoOrigen` y `tipos-ganado` → `tipos-origen`. Tests: `apps/catalogos/tests/test_tipoorigen.py`.

Commit final:

```bash
git commit -m "feat(catalogos): add TipoOrigen CRUD"
```

---

### Task 22: Proveedor CRUD

**Files:**
- Modify: `apps/catalogos/models.py` (añadir `Proveedor`)
- Mismas modificaciones a admin/forms/views/urls
- Create: `templates/catalogos/proveedor_*.html`
- Create: `apps/catalogos/tests/test_proveedor.py`

**Steps:**

- [ ] **Step 22.1: Add model**

```python
class Proveedor(AuditableModel):
    nombre = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    rfc = models.CharField(max_length=13, blank=True, verbose_name="RFC")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    contacto = models.CharField(max_length=80, blank=True, verbose_name="Contacto")
    notas = models.TextField(blank=True, verbose_name="Notas")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
```

- [ ] **Step 22.2: Migrate**

```bash
python manage.py makemigrations catalogos
python manage.py migrate
```

- [ ] **Step 22.3: Admin / Form / Views / URLs**

Mismo patrón que `TipoCorral`. El form lista todos los campos:

```python
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "rfc", "telefono", "contacto", "notas", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "rfc": forms.TextInput(attrs={"class": "input", "maxlength": 13}),
            "telefono": forms.TextInput(attrs={"class": "input"}),
            "contacto": forms.TextInput(attrs={"class": "input"}),
            "notas": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }
```

- [ ] **Step 22.4: Templates**

Lista debe mostrar: nombre, contacto, teléfono, estado.

```html
{# templates/catalogos/proveedor_list.html — solo el bloque de tabla #}
<table class="tbl">
  <thead><tr><th>Nombre</th><th>Contacto</th><th>Teléfono</th><th>Estado</th><th></th></tr></thead>
  <tbody>
    {% for o in objetos %}
      <tr>
        <td>{{ o.nombre }}</td>
        <td>{{ o.contacto|default:"—" }}</td>
        <td>{{ o.telefono|default:"—" }}</td>
        <td><span class="pill {% if o.activo %}pg{% else %}pr{% endif %}">{% if o.activo %}Activo{% else %}Inactivo{% endif %}</span></td>
        <td>
          {% if perms.catalogos.change_proveedor %}<a href="{% url 'catalogos:proveedor_update' o.pk %}" class="btn bo bsm">Editar</a>{% endif %}
          {% if perms.catalogos.delete_proveedor and o.activo %}<a href="{% url 'catalogos:proveedor_delete' o.pk %}" class="btn bo bsm">Eliminar</a>{% endif %}
        </td>
      </tr>
    {% empty %}
      <tr><td colspan="5" style="color:var(--txd);text-align:center;">Sin registros.</td></tr>
    {% endfor %}
  </tbody>
</table>
```

- [ ] **Step 22.5: Tests, run, commit**

```bash
pytest apps/catalogos/tests/test_proveedor.py -v
git add apps/catalogos/ templates/catalogos/proveedor_*
git commit -m "feat(catalogos): add Proveedor CRUD"
```

---

### Task 23: Corral CRUD with `ocupacion_actual` / `disponibilidad`

**Files:**
- Modify: `apps/catalogos/models.py` (añadir `Corral`)
- Mismas modificaciones a admin/forms/views/urls
- Create: `templates/catalogos/corral_*.html`
- Create: `apps/catalogos/tests/test_corral.py`

**Steps:**

- [ ] **Step 23.1: Write failing test**

`apps/catalogos/tests/test_corral.py`:

```python
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def admin_user():
    u = User.objects.create_user(username="admin", email="a@x.com", password="p", is_staff=True)
    u.groups.add(Group.objects.get(name="Administrador"))
    return u


@pytest.mark.django_db
def test_disponibilidad_equals_capacidad_when_empty():
    from apps.catalogos.models import Corral, TipoCorral

    tc = TipoCorral.objects.create(nombre="Engorda")
    c = Corral.objects.create(clave="C25", nombre="Corral 25", tipo_corral=tc, capacidad_maxima=200)
    assert c.ocupacion_actual == 0
    assert c.disponibilidad == 200


@pytest.mark.django_db
def test_corral_clave_unique():
    from apps.catalogos.models import Corral, TipoCorral

    tc = TipoCorral.objects.create(nombre="Engorda")
    Corral.objects.create(clave="C25", nombre="A", tipo_corral=tc, capacidad_maxima=100)
    with pytest.raises(Exception):
        Corral.objects.create(clave="C25", nombre="B", tipo_corral=tc, capacidad_maxima=200)


@pytest.mark.django_db
def test_capacidad_must_be_positive():
    from apps.catalogos.models import Corral, TipoCorral
    from django.core.exceptions import ValidationError

    tc = TipoCorral.objects.create(nombre="Engorda")
    c = Corral(clave="C25", nombre="A", tipo_corral=tc, capacidad_maxima=0)
    with pytest.raises(ValidationError):
        c.full_clean()


def test_admin_creates_corral(client, admin_user):
    from apps.catalogos.models import TipoCorral

    tc = TipoCorral.objects.create(nombre="Engorda")
    client.force_login(admin_user)
    response = client.post(
        reverse("catalogos:corral_create"),
        {"clave": "C25", "nombre": "Corral 25", "tipo_corral": tc.pk, "capacidad_maxima": 200, "activo": "on"},
        follow=True,
    )
    assert response.status_code == 200
    from apps.catalogos.models import Corral

    assert Corral.objects.filter(clave="C25").exists()
```

- [ ] **Step 23.2: Run tests (fail)**

```bash
pytest apps/catalogos/tests/test_corral.py -v
```

- [ ] **Step 23.3: Add model**

```python
from django.core.validators import MinValueValidator


class Corral(AuditableModel):
    clave = models.CharField(max_length=15, unique=True, verbose_name="Clave")
    nombre = models.CharField(max_length=80, verbose_name="Nombre")
    tipo_corral = models.ForeignKey(
        TipoCorral, on_delete=models.PROTECT, related_name="corrales", verbose_name="Tipo de corral"
    )
    capacidad_maxima = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Capacidad máxima"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Corral"
        verbose_name_plural = "Corrales"
        ordering = ["clave"]

    def __str__(self):
        return f"{self.clave} — {self.nombre}"

    @property
    def ocupacion_actual(self) -> int:
        # Spec A: placeholder. Spec B sustituye por suma de inventarios de lotes activos.
        return 0

    @property
    def disponibilidad(self) -> int:
        return self.capacidad_maxima - self.ocupacion_actual
```

- [ ] **Step 23.4: Migrate**

```bash
python manage.py makemigrations catalogos
python manage.py migrate
```

- [ ] **Step 23.5: Admin/Form/Views/URLs/Templates**

Form:

```python
class CorralForm(forms.ModelForm):
    class Meta:
        model = Corral
        fields = ["clave", "nombre", "tipo_corral", "capacidad_maxima", "activo"]
        widgets = {
            "clave": forms.TextInput(attrs={"class": "input"}),
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "capacidad_maxima": forms.NumberInput(attrs={"class": "input", "min": 1}),
        }
```

Views/URLs siguiendo el mismo patrón con `corral_list`, etc.

Lista template muestra columnas: Clave, Nombre, Tipo, Capacidad, Ocupación, Disponibilidad, Estado.

```html
<td>{{ o.clave }}</td><td>{{ o.nombre }}</td>
<td>{{ o.tipo_corral.nombre }}</td>
<td class="mn">{{ o.capacidad_maxima }}</td>
<td class="mn">{{ o.ocupacion_actual }}</td>
<td class="mn">{{ o.disponibilidad }}</td>
```

- [ ] **Step 23.6: Run tests, commit**

```bash
pytest apps/catalogos/tests/test_corral.py -v
git add apps/catalogos/ templates/catalogos/corral_*
git commit -m "feat(catalogos): add Corral CRUD with capacity properties"
```

---

## Phase 6 — ProgramaReimplante (Tasks 24–27)

### Task 24: ProgramaReimplante model with properties and `resolver()`

**Files:**
- Modify: `apps/catalogos/models.py` (añadir `ProgramaReimplante`)
- Create: `apps/catalogos/tests/test_programa_reimplante.py`

**Steps:**

- [ ] **Step 24.1: Write failing tests**

`apps/catalogos/tests/test_programa_reimplante.py`:

```python
"""Tests for ProgramaReimplante model: properties and resolver()."""
from decimal import Decimal

import pytest


@pytest.fixture
def tipos(db):
    from apps.catalogos.models import TipoGanado, TipoOrigen

    return {
        "macho": TipoGanado.objects.create(nombre="Macho"),
        "hembra": TipoGanado.objects.create(nombre="Hembra"),
        "vaca": TipoGanado.objects.create(nombre="Vaca"),
        "corral": TipoOrigen.objects.create(nombre="Corral"),
        "potrero": TipoOrigen.objects.create(nombre="Potrero"),
    }


@pytest.fixture
def programa_machos(tipos):
    from apps.catalogos.models import ProgramaReimplante

    return ProgramaReimplante.objects.create(
        tipo_ganado=tipos["macho"],
        tipo_origen=tipos["corral"],
        peso_min=Decimal("151"),
        peso_max=Decimal("180"),
        gdp_esperada=Decimal("1.35"),
        peso_objetivo_salida=Decimal("580"),
        dias_recepcion=5,
        dias_f1=151,
        dias_transicion=14,
        dias_f3=107,
        dias_zilpaterol=35,
    )


@pytest.fixture
def programa_vacas(tipos):
    """Vaca con tipo_origen=None (comodín)."""
    from apps.catalogos.models import ProgramaReimplante

    return ProgramaReimplante.objects.create(
        tipo_ganado=tipos["vaca"],
        tipo_origen=None,
        peso_min=Decimal("0"),
        peso_max=Decimal("400"),
        gdp_esperada=Decimal("1.60"),
        peso_objetivo_salida=Decimal("485"),
        dias_recepcion=0,
        dias_f1=0,
        dias_transicion=14,
        dias_f3=36,
        dias_zilpaterol=35,
    )


def test_peso_promedio(programa_machos):
    assert programa_machos.peso_promedio == Decimal("165.5")


def test_kg_por_hacer(programa_machos):
    assert programa_machos.kg_por_hacer == Decimal("414.5")


def test_dias_estancia(programa_machos):
    # 414.5 / 1.35 = 307.04 -> int = 307
    assert programa_machos.dias_estancia == 307


def test_total_dias(programa_machos):
    # 5 + 151 + 14 + 107 + 35 = 312
    assert programa_machos.total_dias == 312


def test_resolver_finds_match(programa_machos, tipos):
    from apps.catalogos.models import ProgramaReimplante

    found = ProgramaReimplante.resolver(tipos["macho"], tipos["corral"], Decimal("170"))
    assert found == programa_machos


def test_resolver_returns_none_when_no_match(tipos):
    from apps.catalogos.models import ProgramaReimplante

    assert ProgramaReimplante.resolver(tipos["macho"], tipos["corral"], Decimal("9999")) is None


def test_resolver_falls_back_to_null_origen(programa_vacas, tipos):
    """Vacas se resuelven con tipo_origen=None aunque se pase Corral."""
    from apps.catalogos.models import ProgramaReimplante

    found = ProgramaReimplante.resolver(tipos["vaca"], tipos["corral"], Decimal("350"))
    assert found == programa_vacas


def test_resolver_skips_inactive(programa_machos, tipos):
    from apps.catalogos.models import ProgramaReimplante

    programa_machos.activo = False
    programa_machos.save()
    assert ProgramaReimplante.resolver(tipos["macho"], tipos["corral"], Decimal("170")) is None


def test_history_records_changes(programa_machos):
    programa_machos.gdp_esperada = Decimal("1.40")
    programa_machos.save()
    assert programa_machos.history.count() == 2


def test_check_constraint_peso_max_gt_min(tipos):
    from apps.catalogos.models import ProgramaReimplante
    from django.db.utils import IntegrityError

    with pytest.raises(IntegrityError):
        ProgramaReimplante.objects.create(
            tipo_ganado=tipos["macho"],
            tipo_origen=tipos["corral"],
            peso_min=Decimal("200"),
            peso_max=Decimal("100"),
            gdp_esperada=Decimal("1"),
            peso_objetivo_salida=Decimal("300"),
        )
```

- [ ] **Step 24.2: Run tests (fail)**

```bash
pytest apps/catalogos/tests/test_programa_reimplante.py -v
```

- [ ] **Step 24.3: Implement model**

Append to `apps/catalogos/models.py`:

```python
from django.db.models import F, Q


class ProgramaReimplante(AuditableModel):
    """Motor de cálculo: una fila por (TipoGanado × TipoOrigen × rango de peso)."""

    tipo_ganado = models.ForeignKey(TipoGanado, on_delete=models.PROTECT, verbose_name="Tipo de ganado")
    tipo_origen = models.ForeignKey(
        TipoOrigen,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Tipo de origen",
        help_text="Vacío = aplica a cualquier origen (caso vacas).",
    )

    peso_min = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Peso mínimo")
    peso_max = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Peso máximo")

    gdp_esperada = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="GDP esperada")
    peso_objetivo_salida = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Peso objetivo de salida"
    )

    implante_inicial = models.CharField(max_length=40, blank=True, verbose_name="Implante inicial")
    reimplante_1 = models.CharField(max_length=40, blank=True, verbose_name="1er reimplante")
    reimplante_2 = models.CharField(max_length=40, blank=True, verbose_name="2do reimplante")
    reimplante_3 = models.CharField(max_length=40, blank=True, verbose_name="3er reimplante")
    reimplante_4 = models.CharField(max_length=40, blank=True, verbose_name="4to reimplante")

    dias_recepcion = models.PositiveSmallIntegerField(default=0, verbose_name="Días recepción")
    dias_f1 = models.PositiveSmallIntegerField(default=0, verbose_name="Días F1")
    dias_transicion = models.PositiveSmallIntegerField(default=14, verbose_name="Días transición")
    dias_f3 = models.PositiveSmallIntegerField(default=0, verbose_name="Días F3")
    dias_zilpaterol = models.PositiveSmallIntegerField(default=35, verbose_name="Días Zilpaterol")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Programa de reimplante"
        verbose_name_plural = "Programas de reimplante"
        ordering = ["tipo_ganado__nombre", "tipo_origen__nombre", "peso_min"]
        constraints = [
            models.CheckConstraint(
                check=Q(peso_max__gt=F("peso_min")),
                name="programa_peso_max_gt_min",
            ),
        ]

    def __str__(self):
        origen = self.tipo_origen.nombre if self.tipo_origen else "Cualquiera"
        return f"{self.tipo_ganado.nombre}/{origen} {self.peso_min}-{self.peso_max} kg"

    @property
    def peso_promedio(self):
        return (self.peso_min + self.peso_max) / 2

    @property
    def kg_por_hacer(self):
        return self.peso_objetivo_salida - self.peso_promedio

    @property
    def dias_estancia(self):
        if not self.gdp_esperada:
            return 0
        return int(self.kg_por_hacer / self.gdp_esperada)

    @property
    def total_dias(self):
        return (
            self.dias_recepcion
            + self.dias_f1
            + self.dias_transicion
            + self.dias_f3
            + self.dias_zilpaterol
        )

    @classmethod
    def resolver(cls, tipo_ganado, tipo_origen, peso_inicial):
        """Devuelve la regla aplicable para (tipo_ganado, tipo_origen, peso)."""
        qs = cls.objects.filter(
            activo=True,
            tipo_ganado=tipo_ganado,
            peso_min__lte=peso_inicial,
            peso_max__gte=peso_inicial,
        )
        return qs.filter(tipo_origen=tipo_origen).first() or qs.filter(tipo_origen__isnull=True).first()
```

- [ ] **Step 24.4: Migrate**

```bash
python manage.py makemigrations catalogos
python manage.py migrate
```

- [ ] **Step 24.5: Run tests (pass)**

```bash
pytest apps/catalogos/tests/test_programa_reimplante.py -v
```

Expected: 10 PASS.

- [ ] **Step 24.6: Commit**

```bash
git add apps/catalogos/models.py apps/catalogos/migrations/ apps/catalogos/tests/test_programa_reimplante.py
git commit -m "feat(catalogos): add ProgramaReimplante model with resolver"
```

---

### Task 25: ProgramaReimplante form with overlap validation

**Files:**
- Modify: `apps/catalogos/forms.py`
- Create: `apps/catalogos/tests/test_programa_form.py`

**Steps:**

- [ ] **Step 25.1: Write failing tests**

`apps/catalogos/tests/test_programa_form.py`:

```python
from decimal import Decimal

import pytest


@pytest.fixture
def tipos(db):
    from apps.catalogos.models import TipoGanado, TipoOrigen

    return {
        "macho": TipoGanado.objects.create(nombre="Macho"),
        "corral": TipoOrigen.objects.create(nombre="Corral"),
    }


def _form_data(tipos, peso_min, peso_max):
    return {
        "tipo_ganado": tipos["macho"].pk,
        "tipo_origen": tipos["corral"].pk,
        "peso_min": str(peso_min),
        "peso_max": str(peso_max),
        "gdp_esperada": "1.30",
        "peso_objetivo_salida": "580",
        "dias_recepcion": "5",
        "dias_f1": "100",
        "dias_transicion": "14",
        "dias_f3": "100",
        "dias_zilpaterol": "35",
        "activo": "on",
    }


def test_form_rejects_peso_max_le_min(tipos):
    from apps.catalogos.forms import ProgramaReimplanteForm

    f = ProgramaReimplanteForm(_form_data(tipos, Decimal("200"), Decimal("100")))
    assert not f.is_valid()
    assert "peso_max" in f.errors or "__all__" in f.errors


def test_form_rejects_overlap_with_active_program(tipos):
    from apps.catalogos.forms import ProgramaReimplanteForm
    from apps.catalogos.models import ProgramaReimplante

    ProgramaReimplante.objects.create(
        tipo_ganado=tipos["macho"],
        tipo_origen=tipos["corral"],
        peso_min=Decimal("100"),
        peso_max=Decimal("200"),
        gdp_esperada=Decimal("1"),
        peso_objetivo_salida=Decimal("500"),
    )
    f = ProgramaReimplanteForm(_form_data(tipos, Decimal("180"), Decimal("250")))
    assert not f.is_valid()
    assert "__all__" in f.errors


def test_form_allows_non_overlapping(tipos):
    from apps.catalogos.forms import ProgramaReimplanteForm
    from apps.catalogos.models import ProgramaReimplante

    ProgramaReimplante.objects.create(
        tipo_ganado=tipos["macho"],
        tipo_origen=tipos["corral"],
        peso_min=Decimal("100"),
        peso_max=Decimal("200"),
        gdp_esperada=Decimal("1"),
        peso_objetivo_salida=Decimal("500"),
    )
    f = ProgramaReimplanteForm(_form_data(tipos, Decimal("201"), Decimal("250")))
    assert f.is_valid(), f.errors


def test_form_excludes_self_when_editing(tipos):
    from apps.catalogos.forms import ProgramaReimplanteForm
    from apps.catalogos.models import ProgramaReimplante

    obj = ProgramaReimplante.objects.create(
        tipo_ganado=tipos["macho"],
        tipo_origen=tipos["corral"],
        peso_min=Decimal("100"),
        peso_max=Decimal("200"),
        gdp_esperada=Decimal("1"),
        peso_objetivo_salida=Decimal("500"),
    )
    f = ProgramaReimplanteForm(_form_data(tipos, Decimal("100"), Decimal("200")), instance=obj)
    assert f.is_valid(), f.errors
```

- [ ] **Step 25.2: Run tests (fail)**

```bash
pytest apps/catalogos/tests/test_programa_form.py -v
```

- [ ] **Step 25.3: Add form**

Append to `apps/catalogos/forms.py`:

```python
from django.core.exceptions import ValidationError

from .models import ProgramaReimplante


class ProgramaReimplanteForm(forms.ModelForm):
    class Meta:
        model = ProgramaReimplante
        fields = [
            "tipo_ganado", "tipo_origen", "peso_min", "peso_max",
            "gdp_esperada", "peso_objetivo_salida",
            "implante_inicial", "reimplante_1", "reimplante_2", "reimplante_3", "reimplante_4",
            "dias_recepcion", "dias_f1", "dias_transicion", "dias_f3", "dias_zilpaterol",
            "activo",
        ]
        widgets = {
            "peso_min": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "peso_max": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "gdp_esperada": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "peso_objetivo_salida": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
        }

    def clean(self):
        cd = super().clean()
        peso_min = cd.get("peso_min")
        peso_max = cd.get("peso_max")
        tipo_ganado = cd.get("tipo_ganado")
        tipo_origen = cd.get("tipo_origen")

        if peso_min is not None and peso_max is not None and peso_max <= peso_min:
            raise ValidationError({"peso_max": "Debe ser mayor que peso mínimo."})

        if tipo_ganado and peso_min is not None and peso_max is not None:
            qs = ProgramaReimplante.objects.filter(
                tipo_ganado=tipo_ganado,
                tipo_origen=tipo_origen,
                activo=True,
                peso_min__lte=peso_max,
                peso_max__gte=peso_min,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    "Existe un rango activo que se traslapa con éste para la misma combinación."
                )
        return cd
```

- [ ] **Step 25.4: Run tests (pass)**

```bash
pytest apps/catalogos/tests/test_programa_form.py -v
```

Expected: 4 PASS.

- [ ] **Step 25.5: Commit**

```bash
git add apps/catalogos/forms.py apps/catalogos/tests/test_programa_form.py
git commit -m "feat(catalogos): add ProgramaReimplante form with overlap validation"
```

---

### Task 26: ProgramaReimplante CRUD views and templates

**Files:**
- Modify: `apps/catalogos/admin.py` (registrar)
- Modify: `apps/catalogos/views.py`
- Modify: `apps/catalogos/urls.py`
- Create: `templates/catalogos/programareimplante_list.html`
- Create: `templates/catalogos/programareimplante_form.html`
- Create: `templates/catalogos/programareimplante_detail.html`
- Create: `templates/catalogos/programareimplante_confirm_delete.html`

**Steps:**

- [ ] **Step 26.1: Register admin**

```python
from .models import ProgramaReimplante


@admin.register(ProgramaReimplante)
class ProgramaReimplanteAdmin(SimpleHistoryAdmin):
    list_display = ("tipo_ganado", "tipo_origen", "peso_min", "peso_max", "gdp_esperada", "peso_objetivo_salida", "activo")
    list_filter = ("tipo_ganado", "tipo_origen", "activo")
    search_fields = ("implante_inicial", "reimplante_1")
```

- [ ] **Step 26.2: Add views**

```python
from .forms import ProgramaReimplanteForm
from .models import ProgramaReimplante


class ProgramaReimplanteListView(CatalogoMixin, ListView):
    model = ProgramaReimplante
    template_name = "catalogos/programareimplante_list.html"
    permission_required = "catalogos.view_programareimplante"
    context_object_name = "objetos"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related("tipo_ganado", "tipo_origen")
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        if tg := self.request.GET.get("tipo_ganado"):
            qs = qs.filter(tipo_ganado_id=tg)
        if to := self.request.GET.get("tipo_origen"):
            if to == "null":
                qs = qs.filter(tipo_origen__isnull=True)
            else:
                qs = qs.filter(tipo_origen_id=to)
        return qs

    def get_context_data(self, **kwargs):
        from .models import TipoGanado, TipoOrigen

        ctx = super().get_context_data(**kwargs)
        ctx["tipos_ganado"] = TipoGanado.objects.filter(activo=True)
        ctx["tipos_origen"] = TipoOrigen.objects.filter(activo=True)
        ctx["filtros"] = {
            "tipo_ganado": self.request.GET.get("tipo_ganado", ""),
            "tipo_origen": self.request.GET.get("tipo_origen", ""),
        }
        return ctx


class ProgramaReimplanteCreateView(CatalogoMixin, CreateView):
    model = ProgramaReimplante
    form_class = ProgramaReimplanteForm
    template_name = "catalogos/programareimplante_form.html"
    permission_required = "catalogos.add_programareimplante"
    success_url = reverse_lazy("catalogos:programareimplante_list")


class ProgramaReimplanteUpdateView(CatalogoMixin, UpdateView):
    model = ProgramaReimplante
    form_class = ProgramaReimplanteForm
    template_name = "catalogos/programareimplante_form.html"
    permission_required = "catalogos.change_programareimplante"
    success_url = reverse_lazy("catalogos:programareimplante_list")


class ProgramaReimplanteDetailView(CatalogoMixin, DetailView):
    model = ProgramaReimplante
    template_name = "catalogos/programareimplante_detail.html"
    permission_required = "catalogos.view_programareimplante"
    context_object_name = "obj"


class ProgramaReimplanteDeleteView(CatalogoMixin, View):
    permission_required = "catalogos.delete_programareimplante"

    def get(self, request, pk):
        obj = get_object_or_404(ProgramaReimplante, pk=pk)
        from django.shortcuts import render

        return render(
            request,
            "catalogos/programareimplante_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("catalogos:programareimplante_list")},
        )

    def post(self, request, pk):
        obj = get_object_or_404(ProgramaReimplante, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("catalogos:programareimplante_list")
```

- [ ] **Step 26.3: Add URLs**

```python
    # ProgramaReimplante
    path("programa-reimplantes/", views.ProgramaReimplanteListView.as_view(), name="programareimplante_list"),
    path("programa-reimplantes/nuevo/", views.ProgramaReimplanteCreateView.as_view(), name="programareimplante_create"),
    path("programa-reimplantes/<int:pk>/", views.ProgramaReimplanteDetailView.as_view(), name="programareimplante_detail"),
    path("programa-reimplantes/<int:pk>/editar/", views.ProgramaReimplanteUpdateView.as_view(), name="programareimplante_update"),
    path("programa-reimplantes/<int:pk>/eliminar/", views.ProgramaReimplanteDeleteView.as_view(), name="programareimplante_delete"),
```

- [ ] **Step 26.4: List template with HTMX filter**

`templates/catalogos/programareimplante_list.html`:

```html
{% extends "base.html" %}
{% block title %}Programa de Reimplantes{% endblock %}
{% block content %}
<div class="ph">
  <div><div class="ptitle">Programa de Reimplantes</div><div class="psub">Motor de cálculo del sistema</div></div>
  <div class="bg">
    {% if perms.catalogos.add_programareimplante %}<a href="{% url 'catalogos:programareimplante_create' %}" class="btn bp">+ Nuevo</a>{% endif %}
  </div>
</div>

<div class="card" style="margin-bottom:14px;">
  <form method="get" hx-get="{% url 'catalogos:programareimplante_list' %}" hx-target="#tabla-programa" hx-trigger="change">
    <div class="bg">
      <select name="tipo_ganado" class="input" style="padding:7px;">
        <option value="">Todos los tipos</option>
        {% for t in tipos_ganado %}<option value="{{ t.pk }}" {% if filtros.tipo_ganado == t.pk|stringformat:'s' %}selected{% endif %}>{{ t.nombre }}</option>{% endfor %}
      </select>
      <select name="tipo_origen" class="input" style="padding:7px;">
        <option value="">Cualquier origen</option>
        <option value="null" {% if filtros.tipo_origen == 'null' %}selected{% endif %}>Sin origen (vacas)</option>
        {% for t in tipos_origen %}<option value="{{ t.pk }}" {% if filtros.tipo_origen == t.pk|stringformat:'s' %}selected{% endif %}>{{ t.nombre }}</option>{% endfor %}
      </select>
    </div>
  </form>
</div>

<div class="card" id="tabla-programa">
  <table class="tbl">
    <thead><tr>
      <th>Tipo</th><th>Origen</th><th>Rango (kg)</th><th>GDP</th>
      <th>P. salida</th><th>Días</th><th>Estado</th><th></th>
    </tr></thead>
    <tbody>
      {% for o in objetos %}
        <tr>
          <td>{{ o.tipo_ganado.nombre }}</td>
          <td>{{ o.tipo_origen.nombre|default:"—" }}</td>
          <td class="mn">{{ o.peso_min }} – {{ o.peso_max }}</td>
          <td class="mn">{{ o.gdp_esperada }}</td>
          <td class="mn">{{ o.peso_objetivo_salida }}</td>
          <td class="mn">{{ o.dias_estancia }}</td>
          <td><span class="pill {% if o.activo %}pg{% else %}pr{% endif %}">{% if o.activo %}Activo{% else %}Inactivo{% endif %}</span></td>
          <td>
            {% if perms.catalogos.change_programareimplante %}<a href="{% url 'catalogos:programareimplante_update' o.pk %}" class="btn bo bsm">Editar</a>{% endif %}
            {% if perms.catalogos.delete_programareimplante and o.activo %}<a href="{% url 'catalogos:programareimplante_delete' o.pk %}" class="btn bo bsm">Eliminar</a>{% endif %}
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="8" style="color:var(--txd);text-align:center;">Sin registros con esos filtros.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% include "partials/_pagination.html" %}
{% endblock %}
```

- [ ] **Step 26.5: Form template**

`templates/catalogos/programareimplante_form.html`:

```html
{% extends "base.html" %}
{% block title %}{% if object %}Editar{% else %}Nuevo{% endif %} programa{% endblock %}
{% block content %}
<div class="ph"><div><div class="ptitle">{% if object %}Editar{% else %}Nuevo{% endif %} programa de reimplante</div></div></div>
<div class="card">
  {% include "catalogos/_form.html" with cancel_url=request.META.HTTP_REFERER %}
</div>
{% endblock %}
```

- [ ] **Step 26.6: Detail and confirm_delete templates** (mismo patrón básico)

`templates/catalogos/programareimplante_detail.html`:

```html
{% extends "base.html" %}
{% block content %}
<div class="ph"><div class="ptitle">{{ obj }}</div></div>
<div class="card">
  <div class="g3">
    <div><strong>GDP esperada:</strong> {{ obj.gdp_esperada }}</div>
    <div><strong>Peso objetivo:</strong> {{ obj.peso_objetivo_salida }}</div>
    <div><strong>Días estancia:</strong> {{ obj.dias_estancia }}</div>
    <div><strong>Implante inicial:</strong> {{ obj.implante_inicial|default:"—" }}</div>
    <div><strong>1er reimplante:</strong> {{ obj.reimplante_1|default:"—" }}</div>
    <div><strong>2do reimplante:</strong> {{ obj.reimplante_2|default:"—" }}</div>
    <div><strong>Días F1:</strong> {{ obj.dias_f1 }}</div>
    <div><strong>Días transición:</strong> {{ obj.dias_transicion }}</div>
    <div><strong>Días Zilpaterol:</strong> {{ obj.dias_zilpaterol }}</div>
  </div>
  <div style="margin-top:14px;">
    <a href="{% url 'catalogos:programareimplante_update' obj.pk %}" class="btn bp">Editar</a>
    <a href="{% url 'catalogos:programareimplante_list' %}" class="btn bo">Volver</a>
  </div>
</div>
{% endblock %}
```

`templates/catalogos/programareimplante_confirm_delete.html`:

```html
{% extends "partials/_delete_confirm.html" %}
```

- [ ] **Step 26.7: Smoke test**

```bash
python manage.py runserver
# Visitar /catalogos/programa-reimplantes/
```

- [ ] **Step 26.8: Commit**

```bash
git add apps/catalogos/ templates/catalogos/programareimplante_*
git commit -m "feat(catalogos): add ProgramaReimplante CRUD with htmx filter"
```

---

### Task 27: View test for ProgramaReimplante CRUD with permissions

**Files:**
- Modify: `apps/catalogos/tests/test_programa_reimplante.py` (añadir tests de vista)

**Steps:**

- [ ] **Step 27.1: Append view tests**

```python
@pytest.fixture
def admin_user(db):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group

    U = get_user_model()
    u = U.objects.create_user(username="admin", email="a@x.com", password="p", is_staff=True)
    u.groups.add(Group.objects.get(name="Administrador"))
    return u


@pytest.fixture
def lectura_user(db):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group

    U = get_user_model()
    u = U.objects.create_user(username="lectura", email="l@x.com", password="p")
    u.groups.add(Group.objects.get(name="Solo Lectura"))
    return u


def test_admin_can_list(client, admin_user):
    from django.urls import reverse

    client.force_login(admin_user)
    assert client.get(reverse("catalogos:programareimplante_list")).status_code == 200


def test_lectura_cannot_create(client, lectura_user):
    from django.urls import reverse

    client.force_login(lectura_user)
    assert client.get(reverse("catalogos:programareimplante_create")).status_code == 403


def test_admin_soft_deletes(client, admin_user, programa_machos):
    from django.urls import reverse

    client.force_login(admin_user)
    client.post(reverse("catalogos:programareimplante_delete", args=[programa_machos.pk]))
    programa_machos.refresh_from_db()
    assert programa_machos.activo is False
```

- [ ] **Step 27.2: Run, commit**

```bash
pytest apps/catalogos/tests/test_programa_reimplante.py -v
git add apps/catalogos/tests/test_programa_reimplante.py
git commit -m "test(catalogos): add view permission tests for programa reimplante"
```

---

## Phase 7 — Data migrations / precargas (Tasks 28–31)

### Task 28: Seed TipoCorral · TipoGanado · TipoOrigen

**Files:**
- Create: `apps/catalogos/migrations/0006_seed_tipo_corral.py` (numeración exacta depende del estado de migrations; usar la siguiente disponible)
- Create: `apps/catalogos/migrations/0007_seed_tipo_ganado.py`
- Create: `apps/catalogos/migrations/0008_seed_tipo_origen.py`
- Create: `apps/catalogos/tests/test_seed_tipos.py`

> Numeración: ajustar según el último número que generó `makemigrations` en Tasks 19–24. Asumimos 0006, 0007, 0008. Verificar antes con `ls apps/catalogos/migrations/`.

**Steps:**

- [ ] **Step 28.1: Failing test**

`apps/catalogos/tests/test_seed_tipos.py`:

```python
import pytest


@pytest.mark.django_db
def test_tipo_corral_seeded():
    from apps.catalogos.models import TipoCorral

    nombres = set(TipoCorral.objects.values_list("nombre", flat=True))
    assert {"Recepción", "Engorda", "Zilpaterol"}.issubset(nombres)


@pytest.mark.django_db
def test_tipo_ganado_seeded():
    from apps.catalogos.models import TipoGanado

    nombres = set(TipoGanado.objects.values_list("nombre", flat=True))
    assert {"Macho", "Hembra", "Vaca"}.issubset(nombres)


@pytest.mark.django_db
def test_tipo_origen_seeded():
    from apps.catalogos.models import TipoOrigen

    nombres = set(TipoOrigen.objects.values_list("nombre", flat=True))
    assert {"Corral", "Potrero"}.issubset(nombres)
```

- [ ] **Step 28.2: Verify migration numbers**

```bash
ls apps/catalogos/migrations/
```

- [ ] **Step 28.3: Create seed files**

`apps/catalogos/migrations/000X_seed_tipo_corral.py` (X = siguiente número):

```python
from django.db import migrations

NOMBRES = ["Recepción", "Engorda", "Zilpaterol"]


def forwards(apps, schema_editor):
    TipoCorral = apps.get_model("catalogos", "TipoCorral")
    for nombre in NOMBRES:
        TipoCorral.objects.get_or_create(nombre=nombre)


def backwards(apps, schema_editor):
    TipoCorral = apps.get_model("catalogos", "TipoCorral")
    TipoCorral.objects.filter(nombre__in=NOMBRES).delete()


class Migration(migrations.Migration):
    dependencies = [("catalogos", "PREVIOUS_MIGRATION_NAME")]  # ajustar
    operations = [migrations.RunPython(forwards, backwards)]
```

Análogos para `TipoGanado` (`Macho`, `Hembra`, `Vaca`) y `TipoOrigen` (`Corral`, `Potrero`).

- [ ] **Step 28.4: Apply and test**

```bash
python manage.py migrate catalogos
pytest apps/catalogos/tests/test_seed_tipos.py -v
```

Expected: 3 PASS.

- [ ] **Step 28.5: Commit**

```bash
git add apps/catalogos/migrations/000*_seed_tipo_*.py apps/catalogos/tests/test_seed_tipos.py
git commit -m "feat(catalogos): seed initial TipoCorral, TipoGanado, TipoOrigen"
```

---

### Task 29: Excel reader helper for programa de reimplantes

**Files:**
- Create: `apps/catalogos/seeds/__init__.py`
- Create: `apps/catalogos/seeds/programa_excel.py`
- Create: `apps/catalogos/tests/test_programa_excel_loader.py`

**Steps:**

- [ ] **Step 29.1: Create dirs**

```bash
mkdir -p apps/catalogos/seeds
touch apps/catalogos/seeds/__init__.py
```

- [ ] **Step 29.2: Failing test**

`apps/catalogos/tests/test_programa_excel_loader.py`:

```python
"""Tests for the Excel reader that produces programa rows."""
from pathlib import Path

import pytest


def test_loader_reads_machos_section():
    from apps.catalogos.seeds.programa_excel import leer_programa_excel

    path = Path("docs/DISPONIBILIDAD 2026 1.xlsx")
    rows = leer_programa_excel(path)
    machos = [r for r in rows if r["categoria"] == "MACHOS"]
    assert len(machos) >= 13  # 14 rangos en el Excel; tolerancia
    assert all(r["peso_min"] is not None and r["peso_max"] is not None for r in machos)


def test_loader_reads_vacas_with_null_origen():
    from apps.catalogos.seeds.programa_excel import leer_programa_excel

    path = Path("docs/DISPONIBILIDAD 2026 1.xlsx")
    rows = leer_programa_excel(path)
    vacas = [r for r in rows if r["categoria"] == "VACAS"]
    assert len(vacas) == 2
    assert all(r["tipo_origen"] is None for r in vacas)
```

- [ ] **Step 29.3: Implement loader**

`apps/catalogos/seeds/programa_excel.py`:

```python
"""Reads the PROGRAMA REIMPLANTES sheet and yields normalized rows.

Excel layout: 5 sections with header rows: MACHOS, HEMBRAS, GANADO DE POTRERO MACHO,
GANADO DE POTRERO HEMBRA, VACAS. Each section has its own column structure.

This loader returns a flat list of dicts with the canonical fields used by the
ProgramaReimplante model.
"""
from pathlib import Path

from openpyxl import load_workbook


SECCIONES = {
    "MACHOS": {"tipo_ganado": "Macho", "tipo_origen": "Corral"},
    "HEMBRAS": {"tipo_ganado": "Hembra", "tipo_origen": "Corral"},
    "GANADO DE POTRERO MACHO": {"tipo_ganado": "Macho", "tipo_origen": "Potrero"},
    "GANADO DE POTRERO HEMBRA": {"tipo_ganado": "Hembra", "tipo_origen": "Potrero"},
    "VACAS": {"tipo_ganado": "Vaca", "tipo_origen": None},
}


def _parse_rango(s):
    """'100-150' -> (100, 150). 'MENOR A 400' -> (0, 400). 'MAYOR A 400' -> (400.01, 9999). '511+' -> (511, 9999)."""
    if s is None:
        return None, None
    s = str(s).strip()
    if "MENOR A" in s.upper():
        return 0, int(s.upper().split("MENOR A")[1].strip())
    if "MAYOR A" in s.upper():
        base = int(s.upper().split("MAYOR A")[1].strip())
        return base + 0.01, 9999
    if s.endswith("+"):
        return int(s[:-1]), 9999
    if "-" in s:
        a, b = s.split("-")
        return int(a), int(b)
    return None, None


def leer_programa_excel(path: Path):
    wb = load_workbook(str(path), data_only=True)
    ws = wb["PROGRAMA REIMPLANTES"]
    filas = []
    seccion_actual = None

    for row in ws.iter_rows(values_only=True):
        if not row:
            continue
        first = row[0]
        if isinstance(first, str) and first.strip().upper() in SECCIONES:
            seccion_actual = first.strip().upper()
            continue
        if seccion_actual is None or first is None:
            continue
        if isinstance(first, str) and first.upper().startswith(("RANGO", "PROYECCION", "PROM")):
            continue
        rango = _parse_rango(first)
        if rango[0] is None:
            continue

        meta = SECCIONES[seccion_actual]

        # Las columnas varían por sección; usamos índices conservadores y skipeamos vacíos.
        # Layout machos/hembras/potrero: [rango, prom, kg_hacer, gdp, dias_estancia,
        #   implante, reimp1, reimp2, reimp3, reimp4, recepcion, dias_f1, dias_trans,
        #   dias_f3, dias_z, total_dias, peso_salida]
        try:
            gdp = row[3]
            implante = row[5]
            reimp1 = row[6] if len(row) > 6 else None
            reimp2 = row[7] if len(row) > 7 else None
            reimp3 = row[8] if len(row) > 8 else None
            reimp4 = row[9] if seccion_actual == "MACHOS" and len(row) > 9 else None
            recepcion = row[10] if len(row) > 10 else 0
            dias_f1 = row[11] if len(row) > 11 else 0
            dias_trans = row[12] if len(row) > 12 else 14
            dias_f3 = row[13] if len(row) > 13 else 0
            dias_z = row[14] if len(row) > 14 else 35
            peso_salida = row[16] if len(row) > 16 else 580
        except IndexError:
            continue

        if gdp is None:
            continue

        filas.append({
            "categoria": seccion_actual,
            "tipo_ganado": meta["tipo_ganado"],
            "tipo_origen": meta["tipo_origen"],
            "peso_min": rango[0],
            "peso_max": rango[1],
            "gdp_esperada": gdp,
            "peso_objetivo_salida": peso_salida or 580,
            "implante_inicial": str(implante or "").strip()[:40] if isinstance(implante, str) else "",
            "reimplante_1": str(reimp1 or "").strip()[:40] if isinstance(reimp1, str) and reimp1 != "N/A" else "",
            "reimplante_2": str(reimp2 or "").strip()[:40] if isinstance(reimp2, str) and reimp2 != "N/A" else "",
            "reimplante_3": str(reimp3 or "").strip()[:40] if isinstance(reimp3, str) and reimp3 != "N/A" else "",
            "reimplante_4": str(reimp4 or "").strip()[:40] if isinstance(reimp4, str) and reimp4 != "N/A" else "",
            "dias_recepcion": int(recepcion or 0),
            "dias_f1": int(dias_f1 or 0),
            "dias_transicion": int(dias_trans or 14),
            "dias_f3": int(dias_f3 or 0),
            "dias_zilpaterol": int(dias_z or 35),
        })
    return filas
```

> El parser es heurístico — el Excel actual tiene celdas mergeadas y filas separadoras. Si en el primer run se cargan filas raras, ajustar índices.

- [ ] **Step 29.4: Run tests**

```bash
pytest apps/catalogos/tests/test_programa_excel_loader.py -v
```

Si fallan por desajuste de columnas, **inspeccionar el Excel manualmente con un script ad-hoc** (`python -c "from openpyxl import load_workbook; wb=load_workbook('docs/DISPONIBILIDAD 2026 1.xlsx', data_only=True); ws=wb['PROGRAMA REIMPLANTES']; [print(r) for r in ws.iter_rows(values_only=True)]"`) y ajustar los índices del loader.

- [ ] **Step 29.5: Commit**

```bash
git add apps/catalogos/seeds/ apps/catalogos/tests/test_programa_excel_loader.py
git commit -m "feat(catalogos): add Excel loader for programa de reimplantes"
```

---

### Task 30: Data migration that calls the loader

**Files:**
- Create: `apps/catalogos/migrations/000Y_seed_programa_reimplantes.py` (Y = siguiente número)
- Create: `apps/catalogos/tests/test_seed_programa.py`

**Steps:**

- [ ] **Step 30.1: Failing test**

`apps/catalogos/tests/test_seed_programa.py`:

```python
import pytest


@pytest.mark.django_db
def test_programa_seeded_at_least_40_rows():
    from apps.catalogos.models import ProgramaReimplante

    assert ProgramaReimplante.objects.count() >= 40


@pytest.mark.django_db
def test_programa_vacas_have_null_origen():
    from apps.catalogos.models import ProgramaReimplante, TipoGanado

    vaca = TipoGanado.objects.get(nombre="Vaca")
    assert ProgramaReimplante.objects.filter(tipo_ganado=vaca, tipo_origen__isnull=True).count() >= 2


@pytest.mark.django_db
def test_machos_corral_has_about_14_rows():
    from apps.catalogos.models import ProgramaReimplante, TipoGanado, TipoOrigen

    macho = TipoGanado.objects.get(nombre="Macho")
    corral = TipoOrigen.objects.get(nombre="Corral")
    count = ProgramaReimplante.objects.filter(tipo_ganado=macho, tipo_origen=corral).count()
    assert 12 <= count <= 16
```

- [ ] **Step 30.2: Create data migration**

```python
"""Seed ProgramaReimplante from docs/DISPONIBILIDAD 2026 1.xlsx."""
from pathlib import Path

from django.conf import settings
from django.db import migrations


def forwards(apps, schema_editor):
    from apps.catalogos.seeds.programa_excel import leer_programa_excel

    TipoGanado = apps.get_model("catalogos", "TipoGanado")
    TipoOrigen = apps.get_model("catalogos", "TipoOrigen")
    ProgramaReimplante = apps.get_model("catalogos", "ProgramaReimplante")

    path = Path(settings.BASE_DIR) / "docs" / "DISPONIBILIDAD 2026 1.xlsx"
    if not path.exists():
        return  # No hay archivo; saltar (CI no lo tiene)

    rows = leer_programa_excel(path)

    cache_ganado = {t.nombre: t for t in TipoGanado.objects.all()}
    cache_origen = {t.nombre: t for t in TipoOrigen.objects.all()}

    for r in rows:
        ProgramaReimplante.objects.create(
            tipo_ganado=cache_ganado[r["tipo_ganado"]],
            tipo_origen=cache_origen.get(r["tipo_origen"]) if r["tipo_origen"] else None,
            peso_min=r["peso_min"],
            peso_max=r["peso_max"],
            gdp_esperada=r["gdp_esperada"],
            peso_objetivo_salida=r["peso_objetivo_salida"],
            implante_inicial=r["implante_inicial"],
            reimplante_1=r["reimplante_1"],
            reimplante_2=r["reimplante_2"],
            reimplante_3=r["reimplante_3"],
            reimplante_4=r["reimplante_4"],
            dias_recepcion=r["dias_recepcion"],
            dias_f1=r["dias_f1"],
            dias_transicion=r["dias_transicion"],
            dias_f3=r["dias_f3"],
            dias_zilpaterol=r["dias_zilpaterol"],
        )


def backwards(apps, schema_editor):
    ProgramaReimplante = apps.get_model("catalogos", "ProgramaReimplante")
    ProgramaReimplante.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("catalogos", "PREVIOUS_MIGRATION")]  # ajustar
    operations = [migrations.RunPython(forwards, backwards)]
```

> ⚠️ La precarga depende del archivo Excel en `docs/`. Para CI, ese archivo se debe **commitear al repo** o se debe colocar como artefacto en CI. Si el repo decide NO incluir el Excel, marcar el test del seed como skip cuando no exista el archivo.

- [ ] **Step 30.3: Add Excel to repo (si no está)**

```bash
git add "docs/DISPONIBILIDAD 2026 1.xlsx"
git status
```

- [ ] **Step 30.4: Apply migration**

```bash
python manage.py migrate
```

- [ ] **Step 30.5: Inspect**

```bash
python manage.py shell -c "from apps.catalogos.models import ProgramaReimplante; print(ProgramaReimplante.objects.count(), 'rows'); [print(p) for p in ProgramaReimplante.objects.all()[:5]]"
```

Expected: ~40+ filas. Si las filas se ven mal (e.g., reimplantes con texto raro), revisar el loader en Task 29.

- [ ] **Step 30.6: Run tests**

```bash
pytest apps/catalogos/tests/test_seed_programa.py -v
```

Expected: 3 PASS.

- [ ] **Step 30.7: Commit**

```bash
git add apps/catalogos/migrations/ "docs/DISPONIBILIDAD 2026 1.xlsx" apps/catalogos/tests/test_seed_programa.py
git commit -m "feat(catalogos): seed programa de reimplantes from chamizal excel"
```

---

### Task 31: Permissions enforcement test for Capturista

**Files:**
- Create: `apps/catalogos/tests/test_permisos_capturista.py`

**Steps:**

- [ ] **Step 31.1: Test que Capturista NO puede modificar catálogos del Spec A**

`apps/catalogos/tests/test_permisos_capturista.py`:

```python
"""Capturista en Spec A solo tiene view_*; no puede crear/editar/eliminar catálogos."""
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def capturista(db):
    u = User.objects.create_user(username="capt", email="c@x.com", password="p")
    u.groups.add(Group.objects.get(name="Capturista"))
    return u


def _urls():
    return [
        ("catalogos:tipocorral_create", None),
        ("catalogos:tipoganado_create", None),
        ("catalogos:tipoorigen_create", None),
        ("catalogos:proveedor_create", None),
        ("catalogos:corral_create", None),
        ("catalogos:programareimplante_create", None),
    ]


@pytest.mark.parametrize("urlname,arg", _urls())
def test_capturista_blocked_from_create_views(client, capturista, urlname, arg):
    client.force_login(capturista)
    url = reverse(urlname, args=[arg]) if arg else reverse(urlname)
    response = client.get(url)
    assert response.status_code == 403


def test_capturista_can_view_listings(client, capturista):
    client.force_login(capturista)
    for url in [
        "catalogos:tipocorral_list",
        "catalogos:tipoganado_list",
        "catalogos:tipoorigen_list",
        "catalogos:proveedor_list",
        "catalogos:corral_list",
        "catalogos:programareimplante_list",
    ]:
        assert client.get(reverse(url)).status_code == 200
```

- [ ] **Step 31.2: Run, commit**

```bash
pytest apps/catalogos/tests/test_permisos_capturista.py -v
git add apps/catalogos/tests/test_permisos_capturista.py
git commit -m "test(catalogos): verify capturista cannot modify spec A catalogs"
```

---

## Phase 8 — Polish (Tasks 32–33)

### Task 32: Full coverage run + fix gaps to ≥85%

**Steps:**

- [ ] **Step 32.1: Run full coverage**

```bash
pytest --cov=apps --cov-report=term-missing
```

Expected: cobertura ≥ 85%. Identificar archivos con cobertura baja.

- [ ] **Step 32.2: Add tests for gaps**

Para cada archivo con cobertura < 80%, añadir tests dirigidos a los `Missing` lines reportados. Ejemplos típicos:
- Métodos `__str__` no cubiertos → asserts.
- Branches `else` en formularios → tests con datos contrarios.
- Vista DELETE GET (confirmación) sin test → añadir `client.get(...)` y verificar 200.

- [ ] **Step 32.3: Re-run hasta verde**

```bash
pytest --cov=apps --cov-report=term --cov-fail-under=85
```

Expected: exit 0.

- [ ] **Step 32.4: Commit**

```bash
git add apps/
git commit -m "test: bring coverage to >=85%"
```

---

### Task 33: README + manual smoke checklist + first push

**Files:**
- Modify: `README.md`

**Steps:**

- [ ] **Step 33.1: Expand `README.md`**

Reemplazar `README.md` con la versión final que incluya:

```markdown
# SiCoGa — Sistema Integral de Gestión Ganadera

Sistema web interno para Chamizal Camperos. Centraliza la operación ganadera reemplazando el control manual en Excel.

## Stack

- Python 3.12 · Django 5.1 · MySQL 8.0
- HTMX 1.9 · Alpine.js 3 · CSS portado del dummy v4 (dark mode)
- pytest · factory-boy · django-simple-history · django-environ
- gunicorn · whitenoise (producción)

## Setup local

### Prerequisitos

- Python 3.12 instalado.
- MySQL 8.0 corriendo localmente con un usuario que pueda crear bases de datos.
- (macOS) `brew install mysql-client pkg-config` para compilar `mysqlclient`.

### Pasos

```bash
git clone git@github.com:aleph79/SiCoGa.git
cd SiCoGa
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/dev.txt
pre-commit install
cp .env.example .env
# Editar .env: ajustar DATABASE_URL al MySQL local
mysql -u root -p < scripts/create_db.sql  # si existe; si no, crear DB manualmente
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visitar `http://127.0.0.1:8000/`.

### PyCharm

1. Settings → Project → Python Interpreter → Add → Existing → `./venv/bin/python`.
2. Settings → Languages & Frameworks → Django → Enable: project root, settings = `config/settings/dev.py`, manage.py = `manage.py`.

## Tests

```bash
pytest                                    # todos
pytest apps/catalogos -v                  # solo una app
pytest --cov=apps --cov-report=html       # con cobertura HTML
open htmlcov/index.html
```

## Estructura

- `config/` — settings split (base/dev/prod), URLs, WSGI/ASGI.
- `apps/core/` — modelos abstractos y mixins compartidos.
- `apps/accounts/` — autenticación, usuarios, perfil, roles.
- `apps/catalogos/` — catálogos del sistema (Tipos, Corral, Proveedor, Programa de Reimplantes).
- `templates/` — templates Django (`base.html`, `partials/`, por app).
- `static/` — CSS y JS.
- `docs/` — propuesta, levantamiento de requerimientos, dummy HTML, Excels base.
- `docs/superpowers/specs/` — specs de diseño por entregable.
- `docs/superpowers/plans/` — planes de implementación.

## Roles del sistema

| Grupo | Permisos en Spec A |
|---|---|
| Administrador | Todos. |
| Gerente | `view_*` en todos los modelos. |
| Capturista | `view_*` en catálogos del Spec A (los `add/change` operativos llegan en Specs B/C/D). |
| Solo Lectura | `view_*` en todos los modelos. |

## Despliegue

Producción se hace en el mismo servidor Linux donde corre MiContaAI (sin Docker). El despliegue se documentará al iniciar la fase de QA.

## Documentación

- Propuesta original: `docs/321. Propuesta y cotización Chamizal Camperos.docx`.
- Toma de requerimientos: `docs/Toma de requerimiento especifico Chamizal primera parte.docx`.
- Spec del entregable actual: `docs/superpowers/specs/2026-04-29-sicoga-spec-a-cimientos-design.md`.
- Plan: `docs/superpowers/plans/2026-04-29-sicoga-spec-a-cimientos-plan.md`.
```

- [ ] **Step 33.2: Manual smoke checklist**

Ejecutar manualmente y marcar:

```
[ ] python manage.py runserver levanta sin errores
[ ] / muestra dashboard placeholder con sidebar
[ ] /accounts/login/ funciona (login con superuser)
[ ] /accounts/perfil/ accesible y editable
[ ] Logout regresa a /accounts/login/
[ ] /catalogos/tipos-corral/ lista los 3 tipos seedeados
[ ] /catalogos/tipos-ganado/ lista Macho/Hembra/Vaca
[ ] /catalogos/tipos-origen/ lista Corral/Potrero
[ ] /catalogos/proveedores/ vacío con botón + Nuevo
[ ] /catalogos/corrales/ vacío con botón + Nuevo, dropdown TipoCorral
[ ] /catalogos/programa-reimplantes/ muestra ~40+ filas precargadas
[ ] Filtro HTMX por TipoGanado y TipoOrigen funciona
[ ] /admin/ muestra todos los modelos con icono "history"
[ ] Página 404 se ve estilizada (visitar /no-existe/)
[ ] Login con usuario Capturista: ve listas pero no botón + Nuevo
```

- [ ] **Step 33.3: Final commit**

```bash
git add README.md
git commit -m "docs: finalize README with setup, tests and project map"
```

- [ ] **Step 33.4: Push to GitHub**

```bash
git push -u origin main
```

Expected: CI corre y pasa en verde. Si falla, revisar logs en GitHub Actions.

---

## Self-Review (informe del autor del plan)

**Spec coverage check:**

| Criterio del spec | Tarea(s) que lo cubre |
|---|---|
| 1. `runserver` levanta sin errores | Task 4 + 33 |
| 2. `migrate` aplica todas | Task 4 + cada task con migration |
| 3. 4 grupos de usuarios | Task 12 + test 12.1 |
| 4. Programa precargado | Tasks 29 + 30 + tests |
| 5. Login funciona para 4 roles | Task 11 + tests |
| 6. CRUD para 6 catálogos | Tasks 19, 20, 21, 22, 23, 26 |
| 7. simple_history en modelos | Cada modelo usa `HistoricalRecords()` |
| 8. Capturista no puede crear/editar | Task 31 |
| 9. Sidebar muestra activos + deshabilitados | Task 15 |
| 10. Admin muestra historial | Tasks 19+ usan `SimpleHistoryAdmin` |
| 11. CI pasa en verde | Task 7 + 33.4 |
| 12. pre-commit limpio | Task 6 |
| 13. README documenta setup | Tasks 1 + 33 |
| 14. Páginas 4xx/5xx estilizadas | Task 16 |
| 15. Visual con look del dummy v4 | Task 14 + 15 |

**Placeholder scan:** No hay TBD/TODO sin contenido. Las únicas marcas son intencionales y documentadas en `Corral.ocupacion_actual` (placeholder hasta Spec B) y el dashboard (placeholder hasta Spec F).

**Type consistency:**

- `resolver(tipo_ganado, tipo_origen, peso_inicial)` usado consistentemente en model y tests.
- URL names: convención `<modelo>_<accion>` consistente en todas las tasks.
- `CatalogoMixin.permission_required` set correctamente en cada vista.
- Borrado lógico (`activo=False`) implementado igual en todas las tasks (DeleteView con `post()` que setea atributo).

**Scope check:** Todas las tareas pertenecen al Spec A. Ninguna anticipa Specs B–G.

---

## Execution Handoff

Plan completo y guardado en `docs/superpowers/plans/2026-04-29-sicoga-spec-a-cimientos-plan.md`.

Dos opciones para ejecutarlo:

1. **Subagent-Driven (recomendado)** — Despacho un subagente fresco por tarea, reviso entre tareas, iteración rápida. Skill: `superpowers:subagent-driven-development`.

2. **Inline Execution** — Ejecuto las tareas en esta sesión con `superpowers:executing-plans`, en lotes con checkpoints para revisión.

¿Cuál prefieres?
