#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt

.venv/bin/python <<'CREATE_ENV'
from pathlib import Path
import secrets

path = Path("backend/.env")
if not path.exists():
    template = Path("backend/.env.example").read_text()
    path.write_text(template.replace(
        "DJANGO_SECRET_KEY=",
        "DJANGO_SECRET_KEY=" + secrets.token_urlsafe(50),
        1,
    ))
CREATE_ENV

npm --prefix frontend ci
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py check
echo "Ready. Read docs/development.md to start the servers."
