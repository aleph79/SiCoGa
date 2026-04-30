# Despliegue en producción — SiCoGa

> Guía para instalar SiCoGa Django en el servidor compartido con MiContaAI.
> Servidor: `dedi-1544783.siweb-ia.com` | Usuario cPanel: `sicoga` | Dominio: `sicoga.com` | Ruta: `/home/sicoga/`
> Patrón espejo de la guía de ContaAI (`/workspace/contaai/docs/INSTALACION-DJANGO-CPANEL.md`).

---

## Resumen del stack

| Componente | Valor |
|---|---|
| Sistema | AlmaLinux 9 |
| Panel | WHM / cPanel |
| Web server frontal | EA-nginx (puerto 80/443 público) |
| Runtime | Python 3.12 + Gunicorn |
| Framework | Django 5.1 |
| Base de datos | MySQL Community Edition (gestionada por cPanel) |
| Gestor de procesos | systemd (`sicoga.service`) |
| Puerto interno Gunicorn | **8030** (ContaAI ya usa 8020, no chocan) |
| Firewall | CSF (instalado por cPanel) |
| SSL | AutoSSL de cPanel sobre `sicoga.com` |

---

## FASE 1 — Verificar prerequisitos del sistema

### 1.1 Python 3.12

Ya está instalado en el server (verificado):

```bash
python3.12 --version
which python3.12   # /usr/bin/python3.12
```

### 1.2 Headers para compilar `mysqlclient`

cPanel instala MySQL Community Edition. **No** uses `mysql-devel` — entra en conflicto. Asegura que estos paquetes estén presentes:

```bash
rpm -q mysql-community-devel mysql-community-libs
```

Si falta alguno (poco probable en un cPanel funcional):

```bash
dnf install -y mysql-community-devel mysql-community-libs
```

### 1.3 Resto de dependencias del sistema

```bash
dnf install -y \
    gcc gcc-c++ \
    python3.12-devel \
    libffi-devel \
    openssl-devel \
    libjpeg-devel \
    zlib-devel \
    git
```

> `Pillow` (que SiCoGa usa para `ImageField` del avatar) requiere `libjpeg-devel` y `zlib-devel`.

---

## FASE 2 — Crear base de datos MySQL en cPanel

Accede al cPanel del usuario `sicoga` → **MySQL Databases**.

### 2.1 Crear la base de datos

1. En **Create New Database**, escribe `app` → **Create Database**
2. cPanel la nombrará `sicoga_app` (agrega el prefijo del usuario)

### 2.2 Crear el usuario MySQL

1. En **MySQL Users** → **Add New User**
2. Username: `app` → cPanel lo nombrará `sicoga_app`
3. Genera una contraseña segura → **Create User**

### 2.3 Asignar permisos

1. En **Add User to Database** → selecciona usuario `sicoga_app` y base `sicoga_app`
2. **Add** → selecciona **ALL PRIVILEGES** → **Make Changes**

> Anota la contraseña — la usarás en `DATABASE_URL` del `.env`.

---

## FASE 3 — Clonar e instalar el proyecto

### 3.1 Clonar el repositorio (como `sicoga`)

```bash
su - sicoga
cd /home/sicoga
git clone https://github.com/aleph79/SiCoGa.git sicoga
cd sicoga
```

Estructura resultante:

```
/home/sicoga/sicoga/
├── apps/
├── config/
├── docs/
├── templates/
├── manage.py
├── requirements/
└── .env.example
```

### 3.2 Crear entorno virtual con Python 3.12

```bash
python3.12 -m venv /home/sicoga/venv_sicoga
source /home/sicoga/venv_sicoga/bin/activate
python --version   # Python 3.12.x
which python       # /home/sicoga/venv_sicoga/bin/python
```

### 3.3 Instalar dependencias

```bash
pip install --upgrade pip
pip install -r /home/sicoga/sicoga/requirements/prod.txt
```

> `mysqlclient` viene en `requirements/base.txt` (importado por `prod.txt`). Si la compilación falla, vuelve a la fase 1.2 y verifica los headers.

---

## FASE 4 — Configurar `.env`

```bash
cd /home/sicoga/sicoga
cp .env.example .env
```

### 4.1 Generar `SECRET_KEY`

```bash
source /home/sicoga/venv_sicoga/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4.2 Editar `.env`

```bash
nano .env
```

Contenido completo:

```env
# Django
DEBUG=False
SECRET_KEY=PEGA_AQUI_EL_TOKEN_GENERADO
ALLOWED_HOSTS=sicoga.com,www.sicoga.com
DJANGO_SETTINGS_MODULE=config.settings.prod

# Base de datos (URL estilo django-environ)
DATABASE_URL=mysql://sicoga_app:LA_PASSWORD_QUE_ASIGNASTE@127.0.0.1:3306/sicoga_app

# Email
ADMIN_EMAIL=zgalindo@siwebmx.com
```

> **Importante:** SiCoGa usa `DATABASE_URL` como una sola variable (no `DB_NAME` / `DB_USER` / `DB_PASSWORD` separados como ContaAI). Si la contraseña tiene caracteres especiales (`@`, `:`, `/`), URL-encodéalos.

---

## FASE 5 — Inicializar la base de datos

```bash
cd /home/sicoga/sicoga
source /home/sicoga/venv_sicoga/bin/activate

# Verificar conexión a MySQL antes de migrar
python -c "
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings.prod')
import django; django.setup()
from django.db import connection; connection.ensure_connection()
print('Conexión MySQL OK')
"

# Aplicar migraciones (crea tablas + seeds + carga el Excel automáticamente)
python manage.py migrate

# Crear superusuario administrador
python manage.py createsuperuser

# Recolectar archivos estáticos
mkdir -p logs staticfiles
python manage.py collectstatic --noinput
```

> Las migraciones `0007–0010` cargan los catálogos seed (TipoCorral, TipoGanado, TipoOrigen) y las **49 filas** del programa de reimplante desde `docs/DISPONIBILIDAD 2026 1.xlsx`. No requiere paso manual.

---

## FASE 6 — Probar Gunicorn manualmente

```bash
cd /home/sicoga/sicoga
source /home/sicoga/venv_sicoga/bin/activate

gunicorn \
    --bind 127.0.0.1:8030 \
    --workers 3 \
    config.wsgi:application
```

Si aparece `Listening at: http://127.0.0.1:8030`, todo está bien. `Ctrl+C` para detener.

---

## FASE 7 — Servicio systemd para Gunicorn

Como **root**:

```bash
nano /etc/systemd/system/sicoga.service
```

Contenido:

```ini
[Unit]
Description=SiCoGa Django (Gunicorn)
After=network.target mysqld.service

[Service]
Type=notify
User=sicoga
Group=sicoga
WorkingDirectory=/home/sicoga/sicoga
Environment="PATH=/home/sicoga/venv_sicoga/bin"
EnvironmentFile=/home/sicoga/sicoga/.env
ExecStart=/home/sicoga/venv_sicoga/bin/gunicorn \
    --bind 127.0.0.1:8030 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /home/sicoga/logs/gunicorn-access.log \
    --error-logfile /home/sicoga/logs/gunicorn-error.log \
    config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Crear carpeta de logs (si no se creó en FASE 5)
mkdir -p /home/sicoga/logs
chown sicoga:sicoga /home/sicoga/logs

# Habilitar e iniciar
systemctl daemon-reload
systemctl enable sicoga
systemctl start sicoga
systemctl status sicoga
```

Debe mostrar: `Active: active (running)`.

---

## FASE 8 — Configurar proxy nginx (EA-nginx)

Mismo patrón que ContaAI. nginx público (80/443) sirve `sicoga.com`; el `location /` por defecto va a Apache. Hay que: (1) crear includes para `/static/` y `/media/`, y (2) reemplazar el `location /` principal para que apunte a Gunicorn.

### 8.1 Includes para static y media

```bash
mkdir -p /etc/nginx/conf.d/users/sicoga/sicoga.com
nano /etc/nginx/conf.d/users/sicoga/sicoga.com/sicoga.conf
```

Contenido:

```nginx
location /static/ {
    alias /home/sicoga/sicoga/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /home/sicoga/sicoga/media/;
}
```

### 8.2 Modificar el `location /` principal

```bash
nano /etc/nginx/conf.d/users/sicoga.conf
```

Busca el bloque `location /` dentro del primer `server {}` (el de `sicoga.com`) y reemplázalo por:

```nginx
location / {
    proxy_pass http://127.0.0.1:8030;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300;
}
```

> El header `X-Forwarded-Proto` es **crítico**: sin él, Django no detecta HTTPS y el `SECURE_SSL_REDIRECT=True` de `prod.py` causa loop infinito de redirección.

> **Importante:** cPanel puede regenerar `sicoga.conf` automáticamente al renovar SSL o actualizar EA-nginx. Si el sitio deja de funcionar tras una actualización, repite este paso 8.2.

### 8.3 Verificar y reiniciar nginx

```bash
nginx -t && /scripts/restartsrv_nginx
```

---

## FASE 9 — Permisos y verificación final

```bash
# Permisos
chown -R sicoga:sicoga /home/sicoga/sicoga
chmod -R 755 /home/sicoga/sicoga

# Estado del servicio
systemctl status sicoga

# Prueba directa al gunicorn
curl http://127.0.0.1:8030

# Prueba con dominio
curl -I https://sicoga.com

# Logs en vivo
journalctl -u sicoga -f
```

Abre en navegador: **https://sicoga.com**.

### Smoke checklist (manual)

- [ ] `/` muestra dashboard placeholder.
- [ ] `/accounts/login/` carga.
- [ ] Login con superuser → ves dashboard.
- [ ] `/catalogos/tipos-corral/` lista 3 tipos (Recepción, Engorda, Zilpaterol).
- [ ] `/catalogos/tipos-ganado/` lista Macho/Hembra/Vaca.
- [ ] `/catalogos/tipos-origen/` lista Corral/Potrero.
- [ ] `/catalogos/programa-reimplantes/` muestra **49 filas** precargadas.
- [ ] El filtro HTMX por TipoGanado actualiza la tabla sin recargar.
- [ ] `/admin/` muestra todos los modelos con icono history.

---

## Comandos de operación diaria

```bash
systemctl restart sicoga      # reiniciar
systemctl stop sicoga         # detener
systemctl start sicoga        # iniciar
journalctl -u sicoga -f       # logs en tiempo real
journalctl -u sicoga -n 100   # últimas 100 líneas
```

---

## Actualizaciones futuras

```bash
su - sicoga
cd /home/sicoga/sicoga
source /home/sicoga/venv_sicoga/bin/activate

git pull origin main
pip install -r requirements/prod.txt   # solo si cambiaron dependencias
python manage.py migrate               # solo si hay migraciones nuevas
python manage.py collectstatic --noinput
exit

systemctl restart sicoga
```

---

## Solución de problemas

**502 Bad Gateway:**
```bash
systemctl status sicoga
curl http://127.0.0.1:8030
journalctl -u sicoga -n 50
tail -f /home/sicoga/logs/gunicorn-error.log
```

**Loop de redirección a HTTPS:**
- Verifica que el `proxy_set_header X-Forwarded-Proto $scheme;` esté en el bloque de nginx.
- Verifica que `prod.py` tenga `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` (ya está en el repo).

**Error de conexión a MySQL:**
```bash
source /home/sicoga/venv_sicoga/bin/activate
cd /home/sicoga/sicoga
python -c "
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings.prod')
import django; django.setup()
from django.db import connection; connection.ensure_connection()
print('Conexión MySQL OK')
"
```

Si falla: revisa `DATABASE_URL` en `.env` — caracteres especiales en la contraseña deben URL-encodearse.

**500 Internal Server Error:**
```bash
# Activar DEBUG temporalmente
nano /home/sicoga/sicoga/.env
# DEBUG=False → DEBUG=True
systemctl restart sicoga
# Reproducir el error en navegador, leer traceback, luego volver a DEBUG=False
```

**Estáticos no cargan / 404 en /static/:**
```bash
source /home/sicoga/venv_sicoga/bin/activate
cd /home/sicoga/sicoga
python manage.py collectstatic --noinput
# Verifica que /etc/nginx/conf.d/users/sicoga/sicoga.com/sicoga.conf tenga el alias correcto
nginx -t && /scripts/restartsrv_nginx
```

**Excel no se cargó (programa-reimplantes vacío):**
```bash
# Confirmar que el archivo está en el clone
ls -l /home/sicoga/sicoga/docs/DISPONIBILIDAD\ 2026\ 1.xlsx

# Re-correr la migración 0010
source /home/sicoga/venv_sicoga/bin/activate
python manage.py migrate catalogos 0009  # rollback
python manage.py migrate catalogos       # re-aplicar
```

**Gunicorn no arranca tras reinicio:**
```bash
systemctl is-enabled sicoga   # debe decir "enabled"
systemctl enable sicoga       # si dice "disabled"
```

---

## Resumen de puertos y servicios

| Servicio | Puerto | Exposición |
|---|---|---|
| SiCoGa (Gunicorn/Django) | **8030** | Solo localhost |
| ContaAI (Gunicorn/Django) | 8020 | Solo localhost |
| MySQL | 3306 | Solo localhost |
| nginx HTTP | 80 | Público → redirige a HTTPS |
| nginx HTTPS | 443 | Público → proxy a 8030 |
| cPanel | 2083 | Existente |
| WHM | 2087 | Existente |
