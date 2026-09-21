# NetSage

**Network clarity. Connected communities.**

NetSage is an intelligent network monitoring, predictive risk, incident response, and customer communication platform designed for Internet Service Providers (ISPs).

It helps network operations teams move from reactive troubleshooting to proactive service management by monitoring network telemetry, identifying emerging risk, detecting sustained degradation, correlating related alerts, estimating customer impact, coordinating maintenance response, communicating with customers, receiving customer reports, and verifying network recovery.

NetSage was developed for the **Connecting The Future Hackathon 2026** at Uganda Christian University, Mukono.

---

# The Problem

Internet Service Providers operate complex networks made up of towers, routers, switches, access points, POPs, OLTs, ONTs, and shared upstream connections.

When a network problem occurs, several challenges can appear at the same time:

- Multiple network sites may raise separate alarms even when one shared dependency is responsible.
- Network teams may only become aware of a problem after customers complain.
- Operators may struggle to identify which sites and areas are affected.
- It may be difficult to estimate how many customers are impacted.
- Maintenance escalation may be delayed or inconsistent.
- Customers may receive little or no information while engineers investigate.
- Customer complaints may remain disconnected from technical incidents.
- An incident may be closed before network stability has actually been confirmed.

Traditional monitoring may tell an operator that a device has failed.

NetSage is designed to answer the larger operational questions:

```text
What is happening?

Where is it happening?

Are multiple alerts related?

What shared dependency may be responsible?

Which customers may be affected?

Who should respond?

What should customers be told?

What are customers reporting back?

Has the network actually recovered?
```

---

# The NetSage Solution

NetSage brings network monitoring, incident intelligence, maintenance response, and customer communication into one operational workflow.

```text
Network telemetry
        ↓
Predictive risk analysis
        ↓
Sustained degradation detection
        ↓
Alert generation
        ↓
Multi-site correlation
        ↓
Incident creation
        ↓
Shared dependency reasoning
        ↓
Customer impact analysis
        ↓
Maintenance escalation
        ↓
Engineer investigation
        ↓
Proactive customer communication
        ↓
Customer reports and feedback
        ↓
Recovery verification
        ↓
Service restoration communication
        ↓
Incident resolution
```

The goal is simple:

> **One network problem should not look like three unrelated alarms.**

---

# Core Capabilities

## 1. Multi-Site Network Monitoring

NetSage provides an operations dashboard for monitoring network infrastructure across multiple locations.

The dashboard displays information such as:

- Site health
- Device status
- Latency
- Packet loss
- Reachability
- Active alerts
- Active incidents
- Telemetry history
- Shared dependencies
- Assigned engineers
- Incident activity

This gives network operations teams one place to understand the current state of the network.

---

## 2. Predictive Network Risk

NetSage does not only wait for a complete outage.

The predictive risk engine analyses recent telemetry trends and identifies worsening network conditions while a site may still be reachable.

The prototype considers:

```text
Current latency
Current packet loss
Reachability
Latency trend
Packet loss trend
Consecutive worsening readings
```

A site receives an explainable risk score and level:

```text
Low
Medium
High
Critical
```

Example:

```text
Site: Mukono Central

Risk score: 62/100
Risk level: High
Reachable: Yes
Predicted failure: True
```

This means the network team can begin preventive investigation before complete service failure.

### Explainable Prediction

The current prototype uses a transparent telemetry trend-based risk engine.

Every warning includes reasons such as:

```text
Latency is elevated.
Packet loss is elevated.
Latency is rising rapidly.
Packet loss shows a sustained upward trend.
Latency increased across recent readings.
```

The prototype intentionally avoids presenting prediction as a black-box AI model.

In production, the risk engine can be calibrated with historical ISP telemetry and extended with machine learning models for:

- Failure probability
- Anomaly detection
- Capacity forecasting
- Network behaviour modelling
- Predictive maintenance

---

## 3. Sustained Degradation Detection

NetSage distinguishes between temporary network spikes and sustained problems.

The current demo uses illustrative thresholds such as:

```text
Latency threshold: 150 ms
Packet loss threshold: 5%
Sustained degradation duration: 90 seconds
Expected telemetry interval: 30 seconds
```

A network reading is considered degraded when latency or packet loss exceeds the configured threshold.

An alert is generated only when degradation persists for the required duration.

Production thresholds would be configured together with the ISP's network engineering team.

---

## 4. Multi-Site Incident Correlation

A major NetSage capability is recognizing when several site alerts may represent one underlying network problem.

The demo topology contains:

```text
Mukono Central ─┐
                │
Seeta           ├── Mukono Shared Uplink
                │
UCU Area        ┘
```

If all three sites experience related degradation, NetSage can correlate the alerts into a single incident.

Instead of showing:

```text
Alert 1: Mukono Central
Alert 2: Seeta
Alert 3: UCU Area
```

NetSage presents:

```text
One correlated incident

Affected sites:
- Mukono Central
- Seeta
- UCU Area

Shared dependency:
Mukono Shared Uplink
```

This helps reduce alert noise and gives engineers a clearer operational picture.

---

# Customer Impact Intelligence

NetSage connects network incidents with customers associated with affected sites.

For each incident, the platform can calculate:

```text
Affected sites
Affected areas
Potentially affected customers
SMS-eligible customers
Customer reports received
Reporting customers
Customer impact per site
```

Example:

```text
Affected sites: 3
Affected areas: 3
Potentially affected customers: 6
SMS eligible customers: 1
Customer reports received: 2
```

This allows an ISP to understand the customer impact of a technical problem rather than only seeing infrastructure alarms.

---

# Site-Level Impact Breakdown

NetSage can show customer impact for each affected site individually.

Example:

```text
Mukono Central
Customers: 4
SMS eligible: 1
Reports: 2

Seeta
Customers: 1
SMS eligible: 0
Reports: 0

UCU Area
Customers: 1
SMS eligible: 0
Reports: 0
```

This can help operations teams prioritize response based on actual customer exposure.

---

# Maintenance Escalation

NetSage includes an explainable operational escalation engine.

The recommendation can consider:

```text
Incident severity
Number of affected sites
Number of potentially affected customers
Number of customer reports
```

Supported escalation levels include:

```text
Level 1
Network Operations Centre

Level 2
Regional Network Operations and Maintenance

Level 3
Senior Network Operations and Field Maintenance
```

Example:

```text
Recommended escalation:
Level 2

Team:
Regional Network Operations and Maintenance

Response:
Begin investigation and prepare technician dispatch
if remote recovery is unsuccessful.
```

NetSage records escalation decisions in the incident activity timeline.

Infrastructure-changing actions remain under the control of authorized network engineers.

---

# Incident Response Workflow

NetSage supports the operational lifecycle of an incident.

An operator can:

- Review incident severity
- Review affected sites
- Review probable cause
- Review customer impact
- Review maintenance recommendation
- Assign an engineer
- Start investigation
- Add investigation notes
- View customer reports
- Send customer updates
- Verify recovery
- Resolve the incident

Typical workflow:

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

# Engineer Assignment

Incidents can be assigned to engineers directly from the operations dashboard.

Example:

```text
Incident:
Correlated network degradation affecting
Mukono Central, Seeta, UCU Area

Assigned engineer:
dev_cee

Status:
Investigating
```

This creates clear operational ownership.

---

# Incident Activity Timeline

NetSage records important events throughout an incident.

Timeline events can include:

```text
Incident detected
Engineer assigned
Investigation started
Operator note added
Maintenance escalation
Customer communication
Recovery verified
Incident resolved
```

This creates an operational history that can later support:

- Incident reviews
- Performance analysis
- SLA reporting
- Root cause analysis
- Operations training

---

# Customer Communication

NetSage integrates with **Africa's Talking SMS** to support two-way communication between an ISP and affected customers.

Both directions are supported:

```text
NetSage → Customer

Customer → NetSage
```

This means proactive provider communication does not remove the customer's ability to report problems.

---

# Proactive Customer Notifications

One of the main NetSage goals is to reduce the dependence on customer complaints as the first outage signal.

Once an incident is known, NetSage can identify eligible affected customers and allow the operations team to notify them proactively.

Example:

```text
NetSage Alert:

We detected a network issue affecting
Mukono Central, Seeta and UCU Area.

Our technical team is already investigating.
We will keep you updated.
```

The customer can receive this message before contacting the ISP.

---

# Customer Communication Stages

NetSage supports three main communication stages.

## Outage Notification

Example:

```text
NetSage Alert:

We have detected a connectivity issue affecting your area.
Our technical team has been notified and is investigating.
We will keep you updated.
```

## Progress Update

Example:

```text
Network Update:

Our technical team is investigating the connectivity issue
affecting your area.

Service restoration is in progress.
We will keep you informed.
```

## Recovery Notification

Example:

```text
Service Restored:

Connectivity in your area has recovered.

Thank you for your patience.
```

---

# SMS Approval Workflow

NetSage includes an approval workflow before customer notifications are sent.

```text
Create draft
     ↓
Approve message
     ↓
Send
     ↓
Track delivery
```

This prevents uncontrolled automated messaging while still allowing NetSage to automate audience identification and communication preparation.

---

# SMS Delivery Tracking

Customer notifications can be tracked through states such as:

```text
Not Sent
Dry Run
Queued
Sent
Delivered
Failed
```

NetSage stores provider message identifiers and delivery information where available.

The operations dashboard displays communication activity for each incident.

---

# Customer-to-NetSage SMS

Customers can also report network problems through SMS.

Example:

```text
Customer:

Internet still slow in Mukono
```

Africa's Talking forwards the incoming SMS to NetSage.

NetSage then:

```text
Receives the message
        ↓
Identifies the customer
        ↓
Identifies the customer's site
        ↓
Finds a relevant active incident
        ↓
Links the report to that incident
        ↓
Stores the report
        ↓
Automatically acknowledges the customer
```

Example acknowledgement:

```text
NetSage:

We received your network report.
Our team is checking the issue.

Thank you for letting us know.
```

---

# Customer Reports Dashboard

Incoming customer reports are available to network operations teams.

Reports can contain information such as:

```text
Customer
Phone number
Network site
Message
Related incident
Report status
Time received
```

This allows engineers to combine technical telemetry with customer experience.

A customer complaint therefore becomes part of the incident context rather than remaining isolated inside a customer support channel.

---

# Customer Incident Progress Updates

NetSage can also support customer communication as the incident progresses.

The system can connect incident status changes with customer communication so affected users can remain informed while maintenance work continues.

This creates a communication lifecycle such as:

```text
Incident detected
        ↓
Customer notified
        ↓
Engineer investigates
        ↓
Progress update
        ↓
Customer reports received
        ↓
Recovery verified
        ↓
Service restored notification
```

---

# Africa's Talking Integration

The prototype integrates with the **Africa's Talking Sandbox SMS API**.

The tested outbound flow is:

```text
NetSage
   ↓
Africa's Talking SMS API
   ↓
Sandbox shortcode
   ↓
Customer simulator
```

The tested incoming flow is:

```text
Customer simulator
   ↓
Sandbox shortcode
   ↓
Africa's Talking
   ↓
Public callback
   ↓
ngrok
   ↓
NetSage Django API
   ↓
Customer report matching
   ↓
Automatic acknowledgement
```

This provides a complete two-way SMS communication loop.

---

# SMS Callback Endpoints

## Incoming SMS

```text
POST /api/sms/incoming/
```

## Delivery Reports

```text
POST /api/sms/delivery-report/
```

When running locally, these endpoints can be exposed to Africa's Talking through ngrok.

Example:

```text
https://YOUR-NGROK-DOMAIN/api/sms/incoming/

https://YOUR-NGROK-DOMAIN/api/sms/delivery-report/
```

The ngrok domain may change whenever a new tunnel is started.

Do not hard-code temporary development tunnel URLs into production configuration.

---

# Recovery Verification

NetSage does not consider an incident fixed simply because an engineer believes the problem has been solved.

The recovery engine checks for sustained healthy telemetry across every affected site.

The current demo recovery rules include:

```text
Latency <= 150 ms
Packet loss <= 5%
Healthy period >= 180 seconds
Telemetry interval = 30 seconds
```

For a three-site incident, every affected site must recover.

Example:

```text
Mukono Central → Recovered
Seeta → Recovered
UCU Area → Recovered

Overall recovery:
True
```

Once recovery is verified, the incident can move from:

```text
Investigating
      ↓
Monitoring
```

A recovery notification can then be sent to customers.

---

# Demo Network Topology

The primary NetSage demonstration uses:

```text
Mukono Central
Seeta
UCU Area
```

Shared dependency:

```text
Mukono Shared Uplink
```

Conceptually:

```text
                 INTERNET / CORE NETWORK
                          │
                          │
                Mukono Shared Uplink
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
     Mukono Central      Seeta         UCU Area
           │              │              │
        Customers      Customers      Customers
```

---

# Complete Demo Scenario

The complete NetSage demo can follow this story:

```text
1. Network telemetry is collected.

2. Latency and packet loss begin worsening.

3. NetSage raises an early predictive warning.

4. The site may still be reachable.

5. Degradation becomes sustained.

6. Alerts are generated across multiple sites.

7. NetSage identifies that the sites share
   the Mukono Shared Uplink.

8. Multiple alerts are correlated into one incident.

9. NetSage calculates network and customer impact.

10. A maintenance escalation level is recommended.

11. An engineer is assigned.

12. NetSage can proactively notify affected customers.

13. Customers receive an SMS before needing to complain.

14. Customers can still reply with their own reports.

15. NetSage identifies the customer and site.

16. The report is linked to the existing incident.

17. NetSage automatically acknowledges the customer.

18. Engineers investigate the fault.

19. Progress updates can be communicated to customers.

20. Healthy telemetry returns.

21. NetSage verifies sustained recovery across every site.

22. Customers receive a service restoration message.

23. The incident is resolved.
```

---

# Architecture

```text
                    ISP NETWORK INFRASTRUCTURE
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
      Routers              Switches             OLTs
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                  Telemetry / NMS / SNMP
                              │
                              ▼
                       NETSAGE BACKEND
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    Predictive Risk       Detection          Correlation
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
                       INCIDENT ENGINE
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
 Customer Impact      Maintenance Response     Engineer Workflow
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              │
                              ▼
                    CUSTOMER COMMUNICATION
                              │
                   Africa's Talking SMS
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
             NetSage → Customer   Customer → NetSage
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
                     INCIDENT TIMELINE
                              │
                              ▼
                    RECOVERY VERIFICATION
```

---

# Technology Stack

## Frontend

```text
React
Vite
Tailwind CSS
React Router
Lucide React
Recharts
```

## Backend

```text
Python
Django
Django REST Framework
```

## Database

The hackathon prototype uses:

```text
SQLite
```

A production deployment can use:

```text
PostgreSQL
```

## Messaging

```text
Africa's Talking SMS API
```

## Development Tools

```text
Git
GitHub
ngrok
Docker-ready project structure
```

---

# Hardware and Production Integration

NetSage is primarily a software platform.

It is designed to integrate with infrastructure that ISPs already operate.

Examples include:

```text
Routers
Switches
OLTs
ONTs
Wireless access equipment
Network Management Systems
SNMP-enabled equipment
Syslog sources
Vendor APIs
```

Where additional visibility is needed, an ISP can deploy low-cost edge monitoring hardware such as:

```text
Raspberry Pi monitoring probes
IoT sensors
Power monitoring sensors
Environmental sensors
```

These devices could provide information such as:

```text
Latency
Packet loss
Reachability
Link availability
Power availability
Temperature
Equipment conditions
```

For the hackathon prototype, network telemetry is simulated.

The NetSage application logic processes that telemetry through real application workflows.

---

# Prototype Transparency

The current hackathon prototype uses **simulated network telemetry**.

This allows the team to demonstrate realistic network degradation and recovery scenarios without requiring access to a live ISP network.

Implemented application capabilities include:

```text
Telemetry storage
Predictive risk analysis
Sustained degradation detection
Alert generation
Multi-site incident correlation
Shared dependency reasoning
Incident management
Engineer assignment
Incident timeline
Customer impact calculation
Maintenance escalation
Proactive SMS notifications
SMS approval workflow
SMS delivery tracking
Incoming customer SMS
Customer report matching
Automatic customer acknowledgement
Customer reports dashboard
Customer incident progress updates
Recovery verification
Operational history
```

Production integration would replace or supplement simulated telemetry with real ISP network data.

---

# Production Data Sources

A production version of NetSage could receive telemetry from:

```text
SNMP
Network Management Systems
Router APIs
Switch APIs
OLT/ONT platforms
Syslog
Streaming telemetry
Vendor APIs
Edge monitoring probes
```

---

# Project Structure

```text
netsage/
│
├── backend/
│   │
│   ├── api/
│   │   ├── management/
│   │   │   └── commands/
│   │   │
│   │   ├── migrations/
│   │   │
│   │   ├── services/
│   │   │   ├── customer_incident_updates.py
│   │   │   ├── customer_report_acknowledgement.py
│   │   │   ├── customer_reports.py
│   │   │   ├── predictive_risk.py
│   │   │   ├── recovery.py
│   │   │   ├── simulator_adapter.py
│   │   │   └── sms.py
│   │   │
│   │   ├── delivery_views.py
│   │   ├── impact_views.py
│   │   ├── incoming_views.py
│   │   ├── models.py
│   │   ├── notification_views.py
│   │   ├── operations_views.py
│   │   ├── predictive_views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── config/
│   │
│   └── manage.py
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── marketing/
│   │   │   └── operations/
│   │   │       ├── IncidentImpactPanel.jsx
│   │   │       └── PredictiveRiskPanel.jsx
│   │   │
│   │   ├── pages/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── index.css
│   │
│   └── package.json
│
├── simulator/
│   ├── example_payloads/
│   ├── tests/
│   ├── cli.py
│   ├── detection.py
│   ├── generator.py
│   ├── models.py
│   └── topology.py
│
├── docs/
│
└── README.md
```

---

# Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/netsage-team/netsage.git

cd netsage
```

---

## 2. Create a Python Virtual Environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3. Install Backend Dependencies

Install the backend dependencies defined by the project.

Then verify Django:

```bash
python backend/manage.py check
```

---

## 4. Apply Database Migrations

```bash
python backend/manage.py migrate
```

---

## 5. Seed Demo Data

```bash
python backend/manage.py seed_demo
```

---

## 6. Start the Django Backend

```bash
python backend/manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000/
```

---

## 7. Install Frontend Dependencies

```bash
npm --prefix frontend install
```

---

## 8. Start the Frontend

```bash
npm --prefix frontend run dev
```

Frontend:

```text
http://127.0.0.1:5173/
```

Operations dashboard:

```text
http://127.0.0.1:5173/operations
```

---

# Running the Three Demo Terminals

For SMS integration and local development, three terminals are useful.

## Terminal 1 — Django

```bash
cd ~/Projects/netsage

source .venv/bin/activate

python backend/manage.py runserver
```

## Terminal 2 — React/Vite

```bash
cd ~/Projects/netsage

npm --prefix frontend run dev
```

## Terminal 3 — ngrok

```bash
ngrok http 8000
```

The ngrok URL forwards public webhook requests to:

```text
http://localhost:8000
```

---

# Environment Configuration

Create:

```text
backend/.env
```

Example:

```env
NETSAGE_SMS_MODE=sandbox

AFRICASTALKING_USERNAME=sandbox

AFRICASTALKING_API_KEY=YOUR_SANDBOX_API_KEY

AFRICASTALKING_TEST_RECIPIENTS=+256XXXXXXXXX

AFRICASTALKING_SENDER_ID=YOUR_SANDBOX_SHORTCODE
```

Never commit the real `.env` file or API keys.

The repository should only contain a safe example configuration such as:

```text
backend/.env.example
```

---

# SMS Modes

NetSage supports safe development modes.

## Dry Run

```env
NETSAGE_SMS_MODE=dry_run
```

No external SMS request is made.

This is useful for development and automated testing.

## Africa's Talking Sandbox

```env
NETSAGE_SMS_MODE=sandbox
```

Sandbox mode:

- Uses Africa's Talking sandbox credentials
- Restricts sending to explicitly allowlisted test recipients
- Supports sandbox shortcode testing
- Supports the Africa's Talking Simulator

---

# Africa's Talking Sandbox Setup

Configure the public webhook endpoints in the Africa's Talking Sandbox dashboard.

Example:

```text
Incoming SMS callback:

https://YOUR-NGROK-DOMAIN/api/sms/incoming/
```

```text
Delivery report callback:

https://YOUR-NGROK-DOMAIN/api/sms/delivery-report/
```

The configured sandbox shortcode is used as the outbound sender during simulator testing.

---

# Predictive Warning Demo

Generate worsening but still reachable telemetry:

```bash
python backend/manage.py seed_predictive_warning
```

A successful example can produce:

```text
Predictive warning telemetry created.

Site:
Mukono Central

Risk score:
62/100

Risk level:
high

Predicted failure:
True
```

This demonstrates an important NetSage principle:

> **The provider should not have to wait for complete failure before investigating.**

---

# Incident Correlation Demo

Run:

```bash
python backend/manage.py run_demo_scenario
```

The simulator creates a network scenario involving:

```text
Mukono Central
Seeta
UCU Area
```

NetSage processes the generated telemetry, detects sustained degradation, creates alerts, and correlates the affected sites into an incident.

A successful scenario may report:

```text
Sites: 3
Devices: 3
Telemetry readings: 108
Alerts: 3
Incidents: 1
```

---

# Recovery Demo

The recovery engine expects sustained healthy telemetry.

Demo thresholds:

```text
Latency <= 150 ms
Packet loss <= 5%
Recovery duration >= 180 seconds
```

Recovery is verified across every affected site before the incident can move into monitoring.

---

# Important API Endpoints

## Health

```text
GET /api/health/
```

## Dashboard Summary

```text
GET /api/dashboard/summary/
```

## Sites

```text
GET /api/sites/
```

## Devices

```text
GET /api/devices/
```

## Telemetry

```text
GET /api/telemetry/
```

## Alerts

```text
GET /api/alerts/
```

## Incidents

```text
GET /api/incidents/
```

## Engineers

```text
GET /api/engineers/
```

## Customer Reports

```text
GET /api/customer-reports/
```

## Predictive Risk

```text
GET /api/predictive-risk/
```

## Incident Impact

```text
GET /api/incidents/<incident_id>/impact/
```

## Escalation Update

```text
POST /api/incidents/<incident_id>/impact/
```

## Incoming SMS

```text
POST /api/sms/incoming/
```

## Delivery Report

```text
POST /api/sms/delivery-report/
```

## Notification Workflow

```text
POST /api/notification-draft/

POST /api/notification-approve/

POST /api/notification-send/

GET /api/notification-history/
```

Operational endpoints are protected using application authentication and staff permissions where appropriate.

---

# Testing

Run backend checks:

```bash
python backend/manage.py check
```

Run the backend test suite:

```bash
python backend/manage.py test api
```

At the final integration stage, the NetSage API suite contained:

```text
83 tests
```

and passed successfully.

---

# Frontend Production Build

Run:

```bash
npm --prefix frontend run build
```

The Vite build currently completes successfully.

A large JavaScript bundle warning may appear during the build.

That warning does not prevent the build from succeeding and can be addressed later through code splitting and lazy loading.

---

# Git Validation

Before committing:

```bash
git diff --check
```

Check status:

```bash
git status
```

The repository uses:

```text
feature branches
        ↓
dev
        ↓
main
```

Feature work should normally be merged into `dev` first.

The integrated `dev` branch should be tested before promotion to `main`.

---

# Git Branch Strategy

```text
main
│
└── Stable integrated release
```

```text
dev
│
└── Team integration and testing
```

```text
feature/*
│
└── Individual feature development
```

Typical workflow:

```text
feature branch
      ↓
Pull Request
      ↓
dev
      ↓
Integration testing
      ↓
dev → main Pull Request
      ↓
main
```

---

# Main Product Principles

## Proactive Rather Than Reactive

Customers should not always have to report the outage first.

NetSage aims to identify network risk and incidents as early as possible.

---

## Explainability

Engineers should understand why NetSage:

```text
Raised a warning
Created an alert
Correlated an incident
Recommended an escalation
Verified recovery
```

---

## Customer Awareness

Technical network problems should be connected to customer impact.

NetSage therefore combines:

```text
Infrastructure telemetry
+
Customer records
+
Customer communication
+
Customer reports
```

---

## Human Control

NetSage can automate:

```text
Monitoring
Risk calculation
Detection
Correlation
Impact analysis
Escalation recommendations
Customer audience identification
Customer acknowledgement
Operational history
Recovery evaluation
```

Actions that directly modify network infrastructure should remain under authorized engineer control.

---

## Verified Recovery

An incident should not be considered resolved simply because the alarm disappeared.

NetSage requires healthy telemetry to remain stable for a defined period before declaring recovery.

---

# Current Prototype Capabilities

The current NetSage version includes:

```text
Multi-site monitoring

Telemetry storage

Latency monitoring

Packet loss monitoring

Reachability monitoring

Predictive network risk

Explainable risk scoring

Sustained degradation detection

Alert generation

Multi-site incident correlation

Shared dependency reasoning

Incident severity

Incident timeline

Engineer assignment

Incident notes

Customer records

Customer impact calculation

Site-level customer impact

Maintenance escalation

Automated escalation recommendations

Proactive customer SMS

Outage notifications

Progress notifications

Recovery notifications

SMS approval workflow

SMS delivery tracking

Africa's Talking Sandbox integration

Sandbox shortcode support

Incoming customer SMS

Customer identification

Site identification

Customer-to-incident matching

Automatic customer acknowledgement

Customer reports dashboard

Customer incident progress updates

Recovery verification

Operational history
```

---

# Production Roadmap

A production deployment can extend NetSage with:

```text
Real ISP telemetry integrations

SNMP

Router APIs

Switch APIs

OLT/ONT integrations

Network Management System integrations

Streaming telemetry

Historical telemetry datasets

Machine learning anomaly detection

Advanced predictive maintenance

GIS mapping

Network topology discovery

Maintenance ticket integrations

WhatsApp communication

Voice communication

Email communication

Advanced SLA reporting

Customer portal

Mobile operations application

Multi-tenant ISP support

PostgreSQL

Redis

Background task processing

Cloud deployment

High availability

Observability

Audit logging

Role-based enterprise access
```

---

# Business Model

NetSage is designed as a **B2B SaaS platform for Internet Service Providers**.

Potential pricing models include:

```text
Subscription per monitored site

Subscription per monitored device

ISP-wide enterprise subscription

Integration and onboarding fees

Premium predictive analytics

Advanced operational reporting

Premium support

Communication usage charges
```

---

# Why NetSage Is Different

Many monitoring systems answer:

```text
Which device is currently alarming?
```

NetSage aims to answer:

```text
Is this problem emerging before complete failure?

Are these alerts related?

What dependency connects them?

Which locations are affected?

How many customers may be affected?

Which maintenance team should respond?

Have customers already reported the problem?

Should customers be notified proactively?

What are customers reporting back?

Has the network actually recovered?
```

NetSage therefore connects:

```text
Monitoring
+
Prediction
+
Incident intelligence
+
Customer impact
+
Maintenance response
+
Customer communication
+
Recovery verification
```

into one operational workflow.

---

# Hardware Strategy

NetSage does not require ISPs to replace existing network hardware.

The preferred approach is to integrate first with existing infrastructure such as:

```text
Routers
Switches
OLTs
ONTs
Network Management Systems
```

Where additional independent monitoring is needed, low-cost edge devices such as Raspberry Pi probes or IoT sensors can be deployed.

Example:

```text
ISP Router / OLT
        │
        ├── SNMP
        ├── API
        ├── Syslog
        │
        ▼
Edge Monitoring Probe
        │
        ├── Latency
        ├── Packet loss
        ├── Reachability
        ├── Link health
        └── Power/environment monitoring
        │
        ▼
      NetSage
```

---

# Security and Safety

NetSage uses several safety principles in the prototype.

These include:

```text
Staff-protected operational APIs

Explicit SMS test-recipient allowlists

Sandbox-only external SMS mode

Dry-run SMS support

Human approval for customer notifications

No committed API keys

Environment-based configuration

Human-controlled infrastructure actions
```

Never commit:

```text
backend/.env
```

or real provider credentials.

---

# Team

NetSage was developed collaboratively by:

**Grace Nakiyemba**  
Backend, integration, predictive risk, Operations Interface, incident impact and system integration

**Grace Bawuza**  
Frontend and public product experience

**Phionah Najjuma**  
Simulator and network detection

**Brendalyne Musoki**  
Customer reports and SMS communication

---

# Hackathon

**Connecting The Future Hackathon 2026**

Location:

```text
Uganda Christian University
Mukono, Uganda
```

Theme:

```text
Making telecom networks smarter,
more reliable,
and easier to operate.
```

---

# Vision

NetSage aims to move Internet Service Providers from:

```text
Customer notices outage
        ↓
Customer complains
        ↓
Support receives complaint
        ↓
Operations begins investigation
        ↓
Fault is eventually identified
```

to:

```text
Network risk emerges
        ↓
NetSage detects the trend
        ↓
Operations receives early warning
        ↓
Related network events are correlated
        ↓
Customer impact is identified
        ↓
Maintenance response is coordinated
        ↓
Customers are informed proactively
        ↓
Customer feedback is linked to the incident
        ↓
Recovery is verified
        ↓
Customers are informed of restoration
```

---

# NetSage

## Network clarity. Connected communities.

NetSage turns network signals into coordinated operational action.