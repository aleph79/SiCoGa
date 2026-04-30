---
name: Entorno de desarrollo del usuario
description: Editor, OS y preferencias técnicas operativas del usuario para proyectos Django
type: user
originSessionId: c6a293b1-5224-4046-8975-1bbc90d80f1c
---
- Editor: **PyCharm** (no VSCode). Las configuraciones de proyecto deben ser reconocibles por PyCharm.
- Para entornos Python locales: **virtualenv tradicional** (no Docker para desarrollo). PyCharm debe poder seleccionarlo como interpreter.
- Otro proyecto activo: **MiContaAI**, hospedado en el mismo servidor Linux x86_64 con MySQL 8.0.46. Convenciones de despliegue de SiCoGa replican las de MiContaAI (gunicorn + nginx, sin Docker).
