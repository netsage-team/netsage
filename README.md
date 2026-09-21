# NetSage

**Network clarity. Connected communities.**

NetSage is an intelligent network monitoring and incident response platform designed for Internet Service Providers (ISPs).

It helps network operations teams move from reactive troubleshooting to proactive incident management by monitoring network telemetry, identifying emerging risk, detecting sustained degradation, correlating related site alerts, estimating customer impact, coordinating maintenance response, communicating with customers, and verifying recovery.

NetSage was developed for the **Connecting The Future Hackathon 2026** at Uganda Christian University, Mukono.

---

## The Problem

Internet Service Providers manage networks made up of many towers, routers, access points, POPs, and shared upstream connections.

When a network problem occurs, operations teams may receive several separate alerts from different locations even when those alerts are caused by one shared infrastructure problem.

This creates several challenges:

- Network teams may react only after customers complain.
- Multiple alerts can hide a single underlying incident.
- Operators may struggle to identify which areas are affected.
- It may be difficult to estimate how many customers are impacted.
- Maintenance escalation can be slow or inconsistent.
- Customers may not receive timely service updates.
- Recovery may be assumed before network stability is actually confirmed.

NetSage brings these activities into one operational workflow.

---

## Our Solution

NetSage provides an end-to-end network incident workflow:

```text
Network telemetry
        ↓
Predictive risk analysis
        ↓
Sustained degradation detection
        ↓
Alert generation
        ↓
Multi-site incident correlation
        ↓
Shared dependency reasoning
        ↓
Customer impact analysis
        ↓
Maintenance escalation
        ↓
Customer communication
        ↓
Customer reports
        ↓
Recovery verification
        ↓
Incident resolution
```

Instead of treating every degraded network site as an unrelated problem, NetSage identifies relationships between affected sites and helps operators understand the larger operational picture.

---

## Core Features

### 1. Real-Time Network Monitoring

NetSage monitors network telemetry including:

- Latency
- Packet loss
- Reachability
- Site status
- Device status
- Telemetry history

The operations dashboard provides visibility across multiple network locations.

---

### 2. Predictive Network Risk

NetSage analyses recent telemetry trends to identify potential problems before complete service failure.

The current prototype considers:

- Current latency
- Current packet loss
- Reachability
- Rising latency trends
- Rising packet loss trends
- Consecutive worsening readings

A site receives an explainable risk score and risk level:

```text
Low
Medium
High
Critical
```

For example:

```text
Mukono Central

Risk score: 62/100
Risk level: High
Site reachable: Yes
Predicted failure: True
```

This allows network teams to begin preventive investigation while connectivity still exists.

The hackathon prototype uses an **explainable telemetry trend-based risk engine** rather than a trained black-box machine learning model.

In production, the prediction engine can be calibrated using historical ISP telemetry and extended with machine learning models for anomaly detection and failure probability.

---

### 3. Sustained Degradation Detection

NetSage identifies network problems based on sustained abnormal telemetry rather than reacting to a single temporary spike.

The demo thresholds are illustrative:

```text
Latency threshold: 150 ms
Packet loss threshold: 5%
Sustained degradation duration: 90 seconds
Telemetry interval: 30 seconds
```

These values would be configured together with network engineers in a production deployment.

---

### 4. Incident Correlation

One network problem should not look like three unrelated alarms.

In the NetSage demo topology:

```text
Mukono Central ─┐
Seeta           ├── Mukono Shared Uplink
UCU Area        ┘
```

If all three sites experience related degradation, NetSage can correlate their alerts into one incident and identify the shared upstream dependency as a probable cause indicator.

This helps reduce alert noise and gives engineers a clearer incident context.

---

### 5. Multi-Site Visibility

The operations dashboard shows:

- Healthy sites
- Degraded sites
- Active alerts
- Active incidents
- Shared network dependencies
- Affected locations
- Telemetry trends
- Incident severity
- Assigned engineer
- Incident lifecycle

---

### 6. Customer Impact Analysis

NetSage connects network incidents with customer records associated with affected sites.

For each incident, the platform can calculate:

- Number of affected sites
- Number of affected areas
- Customers potentially affected
- Customers eligible for SMS
- Customer reports received
- Reporting customers
- Site-by-site customer impact

Example:

```text
Affected sites: 3
Potentially affected customers: 6
SMS eligible customers: 1
Customer reports received: 2
```

This allows operations teams to understand both the technical and customer impact of an incident.

---

### 7. Maintenance Escalation

NetSage includes an explainable operational escalation engine.

The recommendation considers:

- Incident severity
- Number of affected sites
- Number of potentially affected customers
- Customer reports

Escalation levels include:

```text
Level 1
Network Operations Centre

Level 2
Regional Network Operations and Maintenance

Level 3
Senior Network Operations and Field Maintenance
```

NetSage can automatically apply operational escalation while infrastructure-changing actions remain under human control.

The platform also records escalation events in the incident timeline.

---

### 8. Engineer Assignment and Incident Workflow

Operators can:

- Assign an engineer
- Start investigation
- Add incident notes
- Review probable causes
- Review affected sites
- Review customer impact
- Monitor maintenance escalation
- Verify recovery
- Resolve incidents

Typical incident lifecycle:

```text
Open
  ↓
Investigating
  ↓
Monitoring Recovery
  ↓
Resolved
```

---

## Customer Communication

NetSage integrates with **Africa's Talking SMS**.

The platform supports both directions of communication.

### NetSage → Customer

NetSage can proactively notify customers before they contact the provider.

Supported communication types include:

```text
Outage notification
Service update
Recovery notification
```

Example proactive message:

```text
NetSage Alert: We detected a network issue affecting your area.
Our technical team is already investigating.
We will keep you updated.
```

This allows the provider to communicate before customers begin calling support.

---

### Customer → NetSage

Customers can also report network problems through SMS.

Example:

```text
Customer:
Internet still slow in Mukono
```

NetSage can:

1. Receive the incoming SMS.
2. Identify the customer from the phone number.
3. Identify the customer's network site.
4. Match the report to an existing active incident.
5. Store the report.
6. Automatically acknowledge the customer.

Example acknowledgement:

```text
NetSage: We received your network report.
Our team is checking the issue.
Thank you for letting us know.
```

This creates a two-way communication loop:

```text
NetSage → Customer
Customer → NetSage
```

---

## Africa's Talking Integration

The hackathon prototype uses the **Africa's Talking Sandbox**.

The tested demo flow is:

```text
NetSage
   ↓
Africa's Talking SMS API
   ↓
Sandbox Shortcode
   ↓
Customer Simulator
```

Incoming communication follows:

```text
Customer Simulator
   ↓
Sandbox Shortcode
   ↓
Africa's Talking
   ↓
Public webhook
   ↓
NetSage
```

For local development, a tool such as **ngrok** can expose the Django webhook endpoints.

### Incoming SMS Callback

```text
/api/sms/incoming/
```

### Delivery Report Callback

```text
/api/sms/delivery-report/
```

The exact public domain changes depending on the development tunnel being used.

---

## Recovery Verification

NetSage does not consider an incident recovered simply because an engineer believes the problem has been fixed.

The platform verifies sustained healthy telemetry across all affected sites.

Current demo recovery conditions include:

```text
Latency <= 150 ms
Packet loss <= 5%
Healthy duration >= 180 seconds
Telemetry interval = 30 seconds
```

All affected sites must satisfy the recovery condition.

Example:

```text
Mukono Central → Recovered
Seeta → Recovered
UCU Area → Recovered
```

After recovery is verified, the incident can move into monitoring and customers can receive a service restoration message.

Example:

```text
Service Restored: Connectivity in your area has recovered.
Thank you for your patience.
```

---

## Demo Network

The main NetSage demonstration uses three sites:

```text
Mukono Central
Seeta
UCU Area
```

Shared dependency:

```text
Mukono Shared Uplink
```

The demo illustrates how one shared infrastructure problem can affect several network locations at the same time.

---

## Demo Story

A typical NetSage live demo follows this sequence:

```text
1. Network is monitored.

2. Telemetry begins worsening.

3. NetSage raises a predictive warning while the site is still reachable.

4. Sustained degradation occurs.

5. Multiple site alerts are generated.

6. NetSage correlates the alerts into one incident.

7. The shared dependency is identified.

8. Customer impact is calculated.

9. Maintenance escalation is recommended or applied.

10. NetSage proactively sends affected customers an SMS.

11. Customers can reply through SMS.

12. Their reports are linked to the existing incident.

13. Engineers investigate the incident.

14. Healthy telemetry returns.

15. NetSage verifies sustained recovery.

16. Customers receive a recovery notification.

17. The incident is resolved.
```

---

## Technology Stack

### Frontend

- React
- Vite
- Tailwind CSS
- React Router
- Lucide React
- Recharts

### Backend

- Python
- Django
- Django REST Framework

### Database

- SQLite for the hackathon prototype
- Production deployments can use PostgreSQL

### Messaging

- Africa's Talking SMS API

### Development and Deployment Tools

- Git
- GitHub
- Docker-ready architecture
- ngrok for local webhook exposure

---

## Architecture

```text
                 NETWORK INFRASTRUCTURE
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
    Routers           Switches          OLTs/ONTs
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
               Telemetry / NMS / SNMP
                         │
                         ▼
                    NETSAGE API
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
       Prediction    Detection    Correlation
            │            │            │
            └────────────┼────────────┘
                         │
                         ▼
                   INCIDENT ENGINE
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
      Customer       Maintenance    Engineer
       Impact        Escalation     Workflow
           │             │             │
           └─────────────┼─────────────┘
                         │
                         ▼
                AFRICA'S TALKING
                         │
                  SMS Communication
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
          ISP → Customer      Customer → ISP
```

---

## Hardware and Production Integration

NetSage is primarily a software platform.

A production implementation can integrate with existing ISP infrastructure such as:

- Routers
- Switches
- OLTs
- ONTs
- Wireless access equipment
- Network Management Systems
- SNMP-enabled infrastructure
- Syslog sources
- Vendor APIs

Where additional visibility is required, low-cost edge monitoring devices can also be deployed.

Examples include:

- Raspberry Pi monitoring probes
- IoT sensors
- Power monitoring devices
- Environmental sensors

These devices could monitor:

- Latency
- Packet loss
- Reachability
- Link availability
- Power availability
- Temperature
- Equipment conditions

For this hackathon prototype, **network telemetry is simulated**.

The NetSage detection, prediction, correlation, database, incident workflow, customer impact analysis, SMS integration, incoming customer reports, maintenance escalation, and recovery verification are implemented application features.

---

## Project Structure

```text
netsage/
│
├── backend/
│   ├── api/
│   │   ├── management/
│   │   ├── migrations/
│   │   ├── services/
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── predictive_views.py
│   │   ├── impact_views.py
│   │   └── incoming_views.py
│   │
│   ├── config/
│   └── manage.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── operations/
│   │   │       ├── PredictiveRiskPanel.jsx
│   │   │       └── IncidentImpactPanel.jsx
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── api.js
│   │
│   └── package.json
│
├── simulator/
│
├── docs/
│
└── README.md
```

---

# Local Development

## 1. Clone the Repository

```bash
git clone https://github.com/netsage-team/netsage.git
cd netsage
```

---

## 2. Create the Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Backend Dependencies

Install the Python dependencies configured for the project.

Then apply migrations:

```bash
python backend/manage.py migrate
```

---

## 4. Seed Demo Data

```bash
python backend/manage.py seed_demo
```

---

## 5. Start Django

```bash
python backend/manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000
```

---

## 6. Install Frontend Dependencies

```bash
npm --prefix frontend install
```

---

## 7. Start the Frontend

```bash
npm --prefix frontend run dev
```

Frontend:

```text
http://127.0.0.1:5173
```

Operations dashboard:

```text
http://127.0.0.1:5173/operations
```

---

## 8. Start ngrok for SMS Webhooks

```bash
ngrok http 8000
```

Configure the resulting public domain in the Africa's Talking Sandbox.

Example:

```text
Incoming SMS:
https://YOUR-NGROK-DOMAIN/api/sms/incoming/

Delivery report:
https://YOUR-NGROK-DOMAIN/api/sms/delivery-report/
```

Never commit temporary ngrok URLs as production configuration.

---

# Environment Variables

Create:

```text
backend/.env
```

Example configuration:

```env
NETSAGE_SMS_MODE=sandbox

AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=YOUR_SANDBOX_API_KEY

AFRICASTALKING_TEST_RECIPIENTS=+256XXXXXXXXX

AFRICASTALKING_SENDER_ID=YOUR_SANDBOX_SHORTCODE
```

Never commit `.env` files or API keys to Git.

For development without external SMS:

```env
NETSAGE_SMS_MODE=dry_run
```

---

# Predictive Warning Demo

To generate worsening but still reachable telemetry:

```bash
python backend/manage.py seed_predictive_warning
```

A demo result may look like:

```text
Site: Mukono Central
Risk score: 62/100
Risk level: high
Predicted failure: True
```

This demonstrates that NetSage can raise a warning before complete network failure.

---

# Incident Demo

Run the existing demo scenario:

```bash
python backend/manage.py run_demo_scenario
```

This simulates network degradation and demonstrates alert detection and incident correlation.

---

# API Highlights

```text
GET  /api/health/

GET  /api/dashboard/summary/

GET  /api/sites/
GET  /api/devices/
GET  /api/telemetry/
GET  /api/alerts/
GET  /api/incidents/

GET  /api/predictive-risk/

GET  /api/incidents/<id>/impact/
POST /api/incidents/<id>/impact/

POST /api/sms/incoming/
POST /api/sms/delivery-report/

POST /api/notification-draft/
POST /api/notification-approve/
POST /api/notification-send/
GET  /api/notification-history/
```

Authenticated operational endpoints are restricted to staff users.

---

# Running Checks

Backend:

```bash
python backend/manage.py check
```

Frontend production build:

```bash
npm --prefix frontend run build
```

Git whitespace check:

```bash
git diff --check
```

---

# Product Principles

NetSage is built around several principles:

### Explainability

Network engineers should understand why a warning or escalation was generated.

### Human-Controlled Infrastructure Actions

NetSage can automate monitoring, correlation, impact analysis, recommendations, escalation, and communication workflows.

Infrastructure-changing remediation should remain controlled by authorized network engineers.

### Customer Communication

Customers should not always have to be the first people to report an outage.

Providers should be able to communicate proactively while still allowing customers to report problems through accessible channels such as SMS.

### Recovery Verification

An incident should not be considered fixed until network telemetry supports that conclusion.

---

# Current Prototype vs Production Deployment

## Implemented in the Prototype

- Multi-site network monitoring
- Simulated telemetry
- Latency and packet loss tracking
- Sustained degradation detection
- Predictive telemetry risk analysis
- Alert generation
- Incident correlation
- Shared dependency reasoning
- Incident lifecycle management
- Engineer assignment
- Incident notes and timeline
- Customer records
- Customer impact analysis
- Maintenance escalation
- Proactive customer SMS
- Incoming customer SMS reports
- Customer-to-incident matching
- Automatic SMS acknowledgements
- Africa's Talking Sandbox integration
- SMS delivery tracking
- Recovery verification
- Operational history

## Production Extensions

A production ISP deployment can add:

- Real SNMP telemetry
- Router integrations
- Switch integrations
- OLT/ONT integrations
- NMS integrations
- Vendor APIs
- Streaming telemetry
- Historical network datasets
- Machine learning models
- Advanced anomaly detection
- Automated maintenance ticketing
- GIS/network topology data
- Additional communication channels
- Advanced reporting and analytics
- High availability deployment
- PostgreSQL
- Cloud infrastructure

---

# Business Model

NetSage is designed as a **B2B SaaS platform for Internet Service Providers**.

Potential commercial models include:

- Subscription per monitored site
- Subscription per monitored device
- ISP-wide enterprise plans
- Integration and onboarding fees
- Premium predictive analytics
- Advanced reporting
- Premium support
- Messaging usage charges

---

# Why NetSage?

Traditional monitoring tools can show that several devices have alarms.

NetSage focuses on turning those signals into an operational response.

Instead of only asking:

```text
Which device is failing?
```

NetSage also helps answer:

```text
Are these alerts related?

What shared dependency may be responsible?

Which locations are affected?

How many customers may be impacted?

Which maintenance team should respond?

Have customers already reported the problem?

Should customers be notified?

Has service actually recovered?
```

That transforms monitoring information into coordinated action.

---

# Team

NetSage was developed collaboratively by:

- **Grace Nakiyemba**
- **Grace Bawuza**
- **Phionah Najjuma**
- **Brendalyne Musoki**

for the **Connecting The Future Hackathon 2026**.

---

# Vision

Our goal is to help Internet Service Providers move from:

```text
Customer complains
        ↓
Operator investigates
        ↓
Fault discovered
```

to:

```text
Network risk detected
        ↓
Operator warned
        ↓
Incident understood
        ↓
Customer impact identified
        ↓
Maintenance coordinated
        ↓
Customers informed
        ↓
Recovery verified
```

---

## NetSage

**Network clarity. Connected communities.**