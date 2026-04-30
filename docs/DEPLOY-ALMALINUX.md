# Instalación en producción — AlmaLinux

Guía paso a paso para montar SiCoGa en un servidor AlmaLinux 10.x con MariaDB 10.11, nginx, gunicorn y Let's Encrypt. Asume el mismo stack que ya corre MiContaAI en el server de Chamizal.

> Ajusta usuario, dominio y rutas según convención del server.

## 1. Paquetes del sistema (como root)

```bash
sudo dnf install -y python3.12 python3.12-devel gcc \
    mariadb-connector-c-devel mariadb \
    nginx git
```

> **No** uses `mysql-devel` — en AlmaLinux/MariaDB el header correcto es `mariadb-connector-c-devel`. Eso es lo que `mysqlclient` enlaza al compilar.

## 2. Usuario y carpeta de la app

```bash
sudo useradd -m -s /bin/bash sicoga
sudo mkdir -p /var/www/sicoga
sudo chown sicoga:sicoga /var/www/sicoga
sudo -iu sicoga
```

## 3. Clonar y crear venv (como `sicoga`)

```bash
cd /var/www/sicoga
git clone git@github.com:aleph79/SiCoGa.git app
cd app
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/prod.txt
```

## 4. Base de datos en MariaDB (como root)

```bash
sudo mysql -u root <<'SQL'
CREATE DATABASE sicoga CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sicoga'@'localhost' IDENTIFIED BY 'CAMBIA-ESTA-CLAVE';
GRANT ALL PRIVILEGES ON sicoga.* TO 'sicoga'@'localhost';
FLUSH PRIVILEGES;
SQL
```

## 5. Configurar `.env` (como `sicoga`)

```bash
cd /var/www/sicoga/app
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(64))"   # genera SECRET_KEY
```

Edita `.env`:

```ini
DEBUG=False
SECRET_KEY=<el token de arriba>
ALLOWED_HOSTS=sicoga.com
DJANGO_SETTINGS_MODULE=config.settings.prod
DATABASE_URL=mysql://sicoga:CAMBIA-ESTA-CLAVE@127.0.0.1:3306/sicoga
ADMIN_EMAIL=zgalindo@siwebmx.com
```

## 6. Migrar, recolectar estáticos y crear superuser

```bash
mkdir -p logs   # prod.py escribe logs/sicoga.log
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

> Las migraciones `0007–0010` cargan los catálogos seed y las **49 filas** del Excel `docs/DISPONIBILIDAD 2026 1.xlsx` automáticamente.

## 7. Gunicorn como servicio systemd (como root)

`/etc/systemd/system/sicoga.service`:

```ini
[Unit]
Description=SiCoGa gunicorn
After=network.target mariadb.service

[Service]
User=sicoga
Group=sicoga
WorkingDirectory=/var/www/sicoga/app
EnvironmentFile=/var/www/sicoga/app/.env
ExecStart=/var/www/sicoga/app/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/sicoga.sock \
    --access-logfile /var/www/sicoga/app/logs/access.log \
    --error-logfile /var/www/sicoga/app/logs/error.log \
    config.wsgi:application
Restart=on-failure
RuntimeDirectory=sicoga

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sicoga
sudo systemctl status sicoga
```

## 8. Nginx vhost (como root)

`/etc/nginx/conf.d/sicoga.conf`:

```nginx
server {
    listen 80;
    server_name sicoga.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sicoga.com;

    # Certbot llenará estos paths
    ssl_certificate     /etc/letsencrypt/live/sicoga.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sicoga.com/privkey.pem;

    client_max_body_size 25M;

    location /static/ {
        alias /var/www/sicoga/app/staticfiles/;
        expires 30d;
    }
    location /media/ {
        alias /var/www/sicoga/app/media/;
    }
    location / {
        proxy_pass http://unix:/run/sicoga.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 9. SSL con Let's Encrypt

```bash
sudo dnf install -y certbot python3-certbot-nginx
sudo certbot --nginx -d sicoga.com
```

## 10. SELinux + firewall (si están activos)

```bash
sudo setsebool -P httpd_can_network_connect 1
sudo chcon -R -t httpd_sys_content_t /var/www/sicoga/app/staticfiles
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --reload
```

## 11. Verificación final

- `curl -I https://sicoga.com` → `200 OK` (o redirect 301 si pegas HTTP).
- `journalctl -u sicoga -f` no muestra tracebacks.
- Login con superuser → ves dashboard.
- `/catalogos/programa-reimplantes/` muestra **49 filas** precargadas.
- `/catalogos/tipos-corral/` muestra los 3 tipos seedeados (Recepción, Engorda, Zilpaterol).

## Deploy de cambios futuros

```bash
sudo -iu sicoga
cd /var/www/sicoga/app
git pull
source venv/bin/activate
pip install -r requirements/prod.txt
python manage.py migrate
python manage.py collectstatic --noinput
exit
sudo systemctl restart sicoga
```

## Notas importantes

- `SECURE_SSL_REDIRECT=True` en `prod.py` **requiere SSL desde el primer arranque**. Si pruebas sin certificado primero, la app redireccionará a HTTPS y fallará. Levanta SSL antes de probar.
- El Excel `docs/DISPONIBILIDAD 2026 1.xlsx` está committeado en el repo, así que `migrate` lo carga sin pasos extra.
- Al cambiar contraseña del usuario MariaDB, recuerda actualizar `.env` y reiniciar `sicoga.service`.
- HSTS está activo (`SECURE_HSTS_SECONDS = 31536000`); una vez que un browser visita el dominio por HTTPS, queda fijado por 1 año. Si haces pruebas con dominios temporales, considera bajar este valor.
