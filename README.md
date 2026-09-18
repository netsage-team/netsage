


NetSage
Network clarity. Connected communities.

NetSage is a network monitoring and incident response platform for Internet Service Providers (ISPs) and network operations teams. It helps operators monitor distributed network infrastructure, detect sustained degradation, correlate related alerts across towers and sites, coordinate incident response, and communicate with customers through Africa's Talking SMS.

Built for the Connecting The Future Hackathon 2026.

Table of Contents
Overview

Key Capabilities

Architecture

Technology Stack

Repository Structure

Developer Setup

Prerequisites

Clone the Repository

Create the Python Environment

Install Backend Dependencies

Configure Environment Variables

Install Frontend Dependencies

Run Database Migrations

Seed Demo Data

Start the Backend

Start the Frontend

Environment Variables

Demo Scenario

Testing and Quality Checks

Africa's Talking SMS Integration

Development Workflow

Troubleshooting

Hackathon Demo Flow

Project Status

Team

Security Notes

License

Overview
Network outages rarely appear as one clear alert.

An ISP may receive alarms from several towers at the same time. Without enough context, an operations team may struggle to determine whether those alarms represent:

independent tower failures

temporary network fluctuations

a single shared upstream fault

an incident already affecting customers

a network event that has actually recovered

NetSage brings these signals into one operational workflow.

Network telemetry
      ↓
Sustained degradation detection
      ↓
Alerts
      ↓
Cross-site correlation
      ↓
Shared dependency analysis
      ↓
Operational incident
      ↓
Engineer investigation
      ↓
Customer communication
      ↓
Recovery verification
      ↓
Incident resolution
A key design principle is:

One network problem should not look like three unrelated alarms.

Key Capabilities
Network Monitoring
NetSage monitors infrastructure conditions such as:

latency

packet loss

availability

device health

site and tower health

Detection logic focuses on sustained degradation rather than treating every short spike as an outage.

Multi-Tower Incident Correlation
NetSage can correlate alerts across several sites and identify when they may share the same dependency.

Example:

Mukono Central ─┐
                │
Seeta ──────────┼── Mukono Shared Uplink
                │
UCU Area ───────┘
Instead of presenting three unrelated incidents, NetSage can group the affected sites into one shared operational event when the evidence supports it.

Infrastructure Topology
The operations interface provides visibility into:

towers and sites

shared infrastructure

active degradation

alert counts

affected sites

shared dependency context

probable cause information

NetSage presents correlated evidence while allowing engineers to verify the actual root cause.

Incident Operations
Operations staff can:

inspect incidents

view affected towers

assign an engineer

add investigation notes

follow incident status

review incident history

verify recovery

resolve incidents

Customer SMS Notifications
NetSage integrates with Africa's Talking and supports:

outage notifications

dry-run mode

sandbox safety

recipient allowlisting

provider message IDs

delivery callbacks

delivery status tracking

Customer Network Issue Reporting
Customers can report network problems through SMS.

Incoming reports are stored as CustomerNetworkReport records and can be connected to customer, site, and incident context as the two-way reporting workflow is completed.

A customer complaint is treated as operational evidence. It should not automatically create a confirmed network outage.

Architecture
┌─────────────────────────────────┐
│          React Frontend         │
│  Public experience + Operations │
└────────────────┬────────────────┘
                 │ HTTP / JSON
                 ▼
┌─────────────────────────────────┐
│       Django REST Backend       │
│                                 │
│ Sites       Devices             │
│ Telemetry   Alerts              │
│ Incidents   Customers           │
│ Notifications                   │
│ Customer Network Reports        │
└────────────────┬────────────────┘
                 │
        ┌────────┴─────────┐
        ▼                  ▼
┌────────────────┐   ┌──────────────────┐
│ Net Simulator  │   │ Africa's Talking │
│                │   │                  │
│ Telemetry      │   │ Outbound SMS     │
│ Detection      │   │ Incoming SMS     │
│ Correlation    │   │ Delivery reports │
│ Recovery       │   └──────────────────┘
└────────────────┘
Technology Stack
Backend
Python

Django 6

Django REST Framework

python-dotenv

dj-database-url

psycopg

Africa's Talking Python SDK

Requests

SQLite for local development data in the repository

PostgreSQL support through DATABASE_URL

Frontend
React 19

React DOM

React Router

Vite 8

Tailwind CSS 4

Recharts

Lucide React

Oxlint

Network Simulation
Python-based deterministic telemetry generation

sustained degradation detection

alert grouping

shared dependency modelling

recovery verification

Development
Git

GitHub

Python virtual environments

npm

Node.js

Repository Structure
netsage/
├── backend/
│   ├── api/                  # Django application and API
│   ├── config/               # Django project configuration
│   ├── .env.example          # Environment variable template
│   ├── db.sqlite3            # Local development database
│   ├── manage.py
│   └── requirements.txt
│
├── docs/
│   ├── development.md
│   └── team.md
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── scripts/
│   └── setup-local.sh
│
├── simulator/
│   ├── tests/
│   ├── cli.py
│   ├── detection.py
│   ├── generator.py
│   ├── models.py
│   ├── topology.py
│   └── README.md
│
├── .gitignore
└── README.md
Developer Setup
The steps below take a new developer from a fresh clone to a working local NetSage environment.

1. Prerequisites
Install:

Git

Python 3.12 or newer

pip

Python venv

Node.js

npm

The team development environment has used Node.js 22 successfully.

Verify your tools:

git --version
python3 --version
pip3 --version
node --version
npm --version
2. Clone the Repository
Clone the project:

git clone https://github.com/netsage-team/netsage.git
cd netsage
For active development, use the shared development branch:

git checkout dev
git pull origin dev
3. Create the Python Environment
From the repository root:

python3 -m venv .venv
source .venv/bin/activate
Your prompt should now show the virtual environment:

(.venv) user@computer:~/Projects/netsage$
Upgrade pip:

python -m pip install --upgrade pip
To leave the environment later:

deactivate
4. Install Backend Dependencies
The backend dependency manifest is:

backend/requirements.txt
Install all backend dependencies with:

pip install -r backend/requirements.txt
The requirements file currently includes the application's Django, REST API, database, environment, HTTP, testing, and Africa's Talking dependencies.

Do not install packages one by one unless you are intentionally changing the project dependency manifest.

5. Configure Environment Variables
Create your local backend environment file from the committed example:

cp backend/.env.example backend/.env
If backend/.env already exists, do not overwrite it unless you intend to replace your local configuration.

Open:

backend/.env
and configure the required values.

The committed template is:

DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=

NETSAGE_SMS_MODE=dry_run
AFRICASTALKING_TEST_RECIPIENTS=
For safe local development, keep:

NETSAGE_SMS_MODE=dry_run
until you intentionally want to test SMS sending.

Never commit your real backend/.env.

6. Install Frontend Dependencies
Because the repository contains both frontend/package.json and frontend/package-lock.json, the recommended clean install is:

npm --prefix frontend ci
If you intentionally update frontend dependencies, use:

npm --prefix frontend install
and review any changes to package-lock.json before committing.

7. Run Database Migrations
With the virtual environment active:

python backend/manage.py migrate
Then verify the Django configuration:

python backend/manage.py check
Check that the models do not require uncommitted migrations:

python backend/manage.py makemigrations --check
A healthy result should include:

No changes detected
System check identified no issues
8. Seed Demo Data
NetSage includes a management command for base demo records:

python backend/manage.py seed_demo
The seed command is designed to prepare predictable demo records while preserving existing records where appropriate.

9. Start the Backend
From the repository root:

source .venv/bin/activate
python backend/manage.py runserver
The Django development server normally starts at:

http://127.0.0.1:8000
Leave this terminal running.

10. Start the Frontend
Open a second terminal and run:

cd /path/to/netsage
npm --prefix frontend run dev
Vite will print the local frontend address, commonly:

http://localhost:5173
Open the URL printed by Vite in your browser.

Quick Start Summary
For a new developer, the complete setup is:

git clone https://github.com/netsage-team/netsage.git
cd netsage

git checkout dev
git pull origin dev

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r backend/requirements.txt

cp backend/.env.example backend/.env

npm --prefix frontend ci

python backend/manage.py migrate
python backend/manage.py check
python backend/manage.py makemigrations --check
python backend/manage.py seed_demo
Then start the backend:

python backend/manage.py runserver
and in another terminal start the frontend:

npm --prefix frontend run dev
Environment Variables
Variable	Purpose	Local Development Guidance
DJANGO_SECRET_KEY	Django cryptographic secret	Set a local development value; use a strong secret in deployed environments
DJANGO_DEBUG	Enables Django debug mode	True locally, False in production
DJANGO_ALLOWED_HOSTS	Allowed Django hostnames	localhost,127.0.0.1 locally
DATABASE_URL	Database connection URL	Configure when using PostgreSQL or another external database
AFRICASTALKING_USERNAME	Africa's Talking application username	Use sandbox for sandbox testing
AFRICASTALKING_API_KEY	Africa's Talking API credential	Required for real sandbox/provider requests; never commit
NETSAGE_SMS_MODE	Controls SMS behaviour	Keep dry_run for safe local development
AFRICASTALKING_TEST_RECIPIENTS	Allowlisted test numbers	Add only approved test recipients
Demo Scenario
NetSage includes a deterministic Mukono network scenario.

Demo Sites
Mukono Central

Seeta

UCU Area

Shared Dependency
Mukono Shared Uplink
The intended scenario is:

Three towers degrade
        ↓
Three network alerts
        ↓
Cross-site correlation
        ↓
One shared incident
        ↓
Shared dependency identified
        ↓
Engineer investigation
        ↓
Customer communication
        ↓
Recovery verification
The scenario is intentionally deterministic so it can be reproduced reliably during development and demonstration.

Testing and Quality Checks
Django Configuration
python backend/manage.py check
Pending Migration Check
python backend/manage.py makemigrations --check
Backend Test Suite
python backend/manage.py test api
Simulator Tests
python -m unittest simulator.tests.test_detection -v
Frontend Lint
npm --prefix frontend run lint
Frontend Production Build
npm --prefix frontend run build
Git Whitespace Check
git diff --check
Recommended Full Validation
Before merging significant work into dev:

python backend/manage.py makemigrations --check
python backend/manage.py check
python backend/manage.py test api
python -m unittest simulator.tests.test_detection -v
npm --prefix frontend run lint
npm --prefix frontend run build
git diff --check
A Vite chunk-size warning does not by itself mean the build failed. Confirm that the build command exits successfully.

Africa's Talking SMS Integration
NetSage uses Africa's Talking for customer communication.

Safe Local Mode
The default template uses:

NETSAGE_SMS_MODE=dry_run
This should remain the default during ordinary local development.

Sandbox Configuration
For Africa's Talking sandbox testing:

AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_sandbox_api_key
AFRICASTALKING_TEST_RECIPIENTS=+2567XXXXXXXX
Use only approved test numbers.

Outbound SMS
The current SMS workflow supports:

controlled outage notifications

provider message IDs

delivery tracking

dry-run mode

sandbox test-recipient restrictions

Delivery Reports
NetSage accepts Africa's Talking delivery callbacks so notification delivery state can be updated.

The development callback route is:

/api/sms/delivery-report/
Typical notification states include:

Pending
Sent
Delivered
Failed
Incoming Customer SMS
NetSage also provides an incoming SMS webhook used to store customer network reports.

The current incoming route is:

/api/sms/incoming/
The incoming message is stored before additional customer/site/incident matching logic is performed.

Local Webhook Testing
Africa's Talking needs a publicly reachable URL for callbacks. During local development, a tunnelling service such as ngrok can expose the Django server.

Example pattern:

https://your-temporary-domain.example/api/sms/delivery-report/
Temporary tunnel domains should never be hardcoded into committed source files.

Development Workflow
NetSage uses this branch flow:

feature branch
      ↓
     dev
      ↓
integration testing
      ↓
     main
Start New Work
Always start from the latest dev:

git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
Example:

git checkout -b feature/customer-report-matching
Commit Changes
git status
git add .
git commit -m "Add customer report matching"
Use a clear commit message describing the change.

Push the Branch
git push -u origin feature/your-feature-name
Open a Pull Request
Active feature pull requests should target:

dev
The final release is:

dev → main
only after integration testing and demo validation are complete.

After a Merge
Update your local development branch:

git checkout dev
git pull origin dev
Then rerun the relevant checks.

Troubleshooting
npm ci Fails
The repository currently includes frontend/package-lock.json, so npm ci should work.

If the lock file and package.json have become inconsistent, do not delete the lock file casually. First inspect the dependency changes. If you are intentionally updating dependencies, run:

npm --prefix frontend install
and review the resulting package-lock.json.

Django Reports Conflicting Migrations
Inspect the migration graph:

python backend/manage.py showmigrations api
Do not randomly delete or rename shared migrations.

When two legitimate branches created parallel migrations, resolve them with a proper Django merge migration.

Django Port Is Already in Use
Run on another port:

python backend/manage.py runserver 8001
Frontend Port Is Already in Use
Vite will usually offer another port. You can also stop the existing process and rerun:

npm --prefix frontend run dev
Frontend Cannot Reach the Backend
Check:

Django is running

the frontend API base URL is correct

Django allowed hosts

CORS configuration

browser Network tab

browser console

Django terminal logs

SMS Is Not Sending
Check:

AFRICASTALKING_USERNAME

AFRICASTALKING_API_KEY

NETSAGE_SMS_MODE

AFRICASTALKING_TEST_RECIPIENTS

recipient phone-number format

Africa's Talking sandbox configuration

provider response

delivery callback logs

Do not print or commit the API key while debugging.

Hackathon Demo Flow
The intended complete NetSage demonstration is:

Public NetSage Website
        ↓
Operations Dashboard
        ↓
Mukono Shared Uplink Scenario
        ↓
Three Towers Degrade
        ↓
Alerts Are Correlated
        ↓
One Shared Incident Appears
        ↓
Engineer Investigates
        ↓
Customer Outage SMS
        ↓
SMS Delivery Tracking
        ↓
Customer Reports Network Problem
        ↓
Report Matched To Operational Context
        ↓
Acknowledgement / Progress Communication
        ↓
Network Recovers
        ↓
Recovery Verified
        ↓
Customer Recovery Update
        ↓
Incident Resolved
Features still under active development should not be presented as complete until they are merged into dev and validated.

Project Status
NetSage is under active development for the Connecting The Future Hackathon 2026.

Integrated in dev
network telemetry simulation

sustained degradation detection

cross-site alert correlation

deterministic Mukono scenario

incident creation and operations workflow

engineer assignment and incident timeline

tower infrastructure monitoring

network topology visualization

outbound customer SMS notifications

delivery tracking and callbacks

incoming customer SMS webhook

customer network report storage

In Progress
customer/site/incident report matching

automatic SMS acknowledgement

customer progress and recovery updates

customer reports dashboard

public NetSage website

product/demo entry experience

responsive design

accessibility and final polish

Team
Grace Nakiyemba
Core Backend, Operations Interface, Technical Lead and Integration


operations dashboard

incident visibility

operational workflows

backend architecture

Django APIs

incident operations

system integration

SMS integration

final QA and release integration

Phionah Najjuma
Network Simulation and Detection

telemetry simulation

degradation detection

network scenarios

correlation support


Brendalyne Musoki
Customer Communication and SMS

customer network reports

incoming SMS

customer communication workflows

Grace Bawuza
Public Website and Product Experience

public website

product storytelling

visual system

demo entry experience

responsive design

Security Notes
Never commit backend/.env

Never commit Africa's Talking API keys

Keep secrets in environment variables

Use NETSAGE_SMS_MODE=dry_run for ordinary local development

Preserve sandbox recipient restrictions

Mask customer phone numbers in staff interfaces where possible

Do not expose private customer data through public endpoints

Treat customer reports as evidence rather than automatic proof of an outage

Use DJANGO_DEBUG=False in deployed production environments

Use a strong DJANGO_SECRET_KEY outside local development

License
See the repository LICENSE file for licensing information