---
name: Entorno de desarrollo alterno - AlmaLinux box
description: Servidor Linux x86_64 (AlmaLinux 10.1) usado como entorno alterno de SiCoGa, con MariaDB en lugar del MySQL 8.0.46 canónico, y los paquetes de sistema necesarios para compilar mysqlclient
type: user
---
Hay un segundo equipo de desarrollo además del mac de Zeus (`/Users/zeus/Documents/Fuentes/Django/SiCoGa`):

- **OS**: AlmaLinux 10.1 (Heliotrope Lion), `el10`, RHEL-derivado. `dnf`/`yum` disponibles, no `apt`.
- **Working dir**: `/workspace/sicoga`
- **DB engine**: **MariaDB 10.11.15-MariaDB**, NO el MySQL 8.0.46 del stack canónico. Cliente compatible con `mysqlclient`/Django pero hay que tenerlo presente si aparecen sutilezas de SQL.
- **Credenciales locales**: `root/solsticio`. BDs `sicoga_dev` y `sicoga_test` ya creadas con `utf8mb4_unicode_ci`.

**Paquetes de sistema requeridos antes del `pip install -r requirements/dev.txt`** (compilación de `mysqlclient`):

```
dnf install -y gcc python3.12-devel mariadb-connector-c-devel pkgconf-pkg-config
```

Sin estos, `pip install mysqlclient` falla con `Exception: Can not find valid pkg-config name`.

**Why:** En este equipo (root, pero AlmaLinux mínimo) no venían instaladas las dev libs de MariaDB ni `gcc`, y `mysqlclient` se construye desde sdist porque no hay wheel binario para esta combinación de Python + libc. Documentarlo evita re-diagnosticar el mismo error la próxima vez que se monte una caja AlmaLinux desde cero.

**How to apply:**
- Al iniciar sesión en `/workspace/sicoga` ya no hace falta reinstalar — `venv/` está poblado con todas las deps. Sólo `source venv/bin/activate`.
- Si alguna vez se levanta otra caja AlmaLinux (o se borra el venv), correr el `dnf install` de arriba ANTES del `pip install`.
- Si una migración/test falla con un error que sólo se reproduce aquí, sospechar primero del cambio MySQL 8.0 → MariaDB 10.11 (p.ej. funciones JSON, modos SQL estrictos, CHECK constraints más estrictos en MariaDB).
