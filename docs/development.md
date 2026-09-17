# NetSage development

## Requirements
Node.js 24 LTS, npm, Python 3.12 to 3.14 with venv support, and Git.

## Install
Run from the repository root:

    bash scripts/setup-local.sh

## Start the backend in terminal one

    .venv/bin/python backend/manage.py runserver 127.0.0.1:8000

## Start the frontend in terminal two

    npm --prefix frontend run dev

Open http://127.0.0.1:5173 and click Check backend.

## Database
SQLite is used locally by default.
For PostgreSQL, create a database, set DATABASE_URL in backend/.env,
and run migrations again. This does not transfer existing SQLite data.

## Messaging
The Africa's Talking Python SDK is installed.
Sandbox credentials belong in backend/.env.
SMS sending and delivery callbacks still need implementation.

## Collaboration
Read docs/team.md for proposed responsibilities.
Create a feature branch from the latest main.
Open a pull request into main for Grace256c to review and merge.

## Scope
This foundation includes the frontend, backend, and API health check.
Monitoring, simulation, incident management, SMS, and recovery
verification remain implementation tasks.

The Vite API proxy is for local development.
Production hosting needs its own routing and security configuration.
