#!/bin/bash
# Deploy de cambios en producción (cPanel/AlmaLinux + gunicorn + systemd).
#
# Uso (como root en el server):
#   sudo bash /home/sicoga/sicoga/scripts/update.sh
#
# Lo que hace:
#   1. git pull (como sicoga)
#   2. pip install -r requirements/prod.txt (sólo si cambió)
#   3. python manage.py migrate
#   4. python manage.py collectstatic --noinput
#   5. systemctl restart sicoga
#
# Idempotente y seguro de ejecutar varias veces.

set -euo pipefail

APP_USER="sicoga"
APP_DIR="/home/sicoga/sicoga"
VENV_DIR="/home/sicoga/venv_sicoga"
SERVICE="sicoga"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: corre este script como root (necesita systemctl restart)." >&2
    exit 1
fi

if [ ! -d "$APP_DIR" ]; then
    echo "ERROR: no existe $APP_DIR. ¿Primera instalación? Sigue docs/DEPLOY-ALMALINUX.md." >&2
    exit 1
fi

echo "==> git pull"
sudo -u "$APP_USER" git -C "$APP_DIR" pull --ff-only origin main

echo "==> pip install (prod)"
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements/prod.txt"

echo "==> migrate"
sudo -u "$APP_USER" bash -c "cd '$APP_DIR' && '$VENV_DIR/bin/python' manage.py migrate"

echo "==> collectstatic"
sudo -u "$APP_USER" bash -c "cd '$APP_DIR' && '$VENV_DIR/bin/python' manage.py collectstatic --noinput"

echo "==> restart $SERVICE"
systemctl restart "$SERVICE"
sleep 2
systemctl is-active --quiet "$SERVICE" && echo "OK: $SERVICE activo" || {
    echo "ERROR: $SERVICE no arrancó. Revisa: journalctl -u $SERVICE -n 50" >&2
    exit 1
}

echo "==> Smoke HTTP"
HTTP_STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" "https://sicoga.com/" || true)
if [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "200" ]; then
    echo "OK: https://sicoga.com/ → $HTTP_STATUS"
else
    echo "ADVERTENCIA: https://sicoga.com/ → $HTTP_STATUS (esperaba 302 o 200)" >&2
fi

echo
echo "Deploy completo."
