# ai-receptionist
# Self-Healing Web Application

A local-first, Docker Compose–orchestrated web application that detects its own failure and recovers automatically. Built with Flask, Nginx, Prometheus, and Grafana.

## Architecture

┌─────────────────────────────────────────────────────┐
│ monitoring (bridge network) │
│ │
│ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│ │ Nginx │───▶│ Flask │◀───│ Prometheus │ │
│ │ :80 │ │ :5000 │ │ :9090 │ │
│ └──────────┘ └──────────┘ └──────┬───────┘ │
│ │ │
│ ┌──────▼───────┐ │
│ │ Grafana │ │
│ │ :3000 │ │
│ └──────────────┘ │
└─────────────────────────────────────────────────────┘


| Service | Image / Build | Role |
|---------|--------------|------|
| `web-app` | Custom (Flask) | The application that "dies" and heals |
| `nginx-proxy` | `nginx:latest` | Reverse proxy / traffic routing |
| `prometheus` | `prom/prometheus:latest` | Scrapes metrics, fires alerts |
| `grafana` | `grafana/grafana:latest` | Visualization dashboard |

## How It Works

1. **Prometheus** scrapes `web-app:5000/metrics` every 5 seconds.
2. If the app is unreachable, the `up` metric drops to `0`.
3. After **5 seconds** of sustained `up == 0`, the `ServiceDown` alert fires.
4. **Docker** detects the container is stopped and restarts it (`restart: always`).
5. The health check confirms the app is back, Prometheus sees `up == 1`, and the alert resolves.

Total downtime: **~5–10 seconds. No human intervention required.**

## Directory Structure

self-healing-app/
├── app/
│ ├── app.py # Flask application
│ └── Dockerfile
├── nginx/
│ └── nginx.conf # Reverse proxy config
├── prometheus/
│ ├── prometheus.yml # Scrape config
│ └── alert.rules.yml # Alerting rules
└── docker-compose.yml # Orchestration


## Prerequisites

- Docker Engine + Docker Compose v2 (`docker compose`)
- Git (with `user.name` and `user.email` configured)
- Ports 80, 3000, 5000, 9090 free on your machine

> If system nginx is running: `sudo systemctl stop nginx && sudo systemctl disable nginx`

## Quick Start

```bash
# Clone / enter the project directory
cd self-healing-app

# Build and start all services
docker compose up --build -d

# Verify everything is running
docker compose ps

Accessing Services
Service	URL	Credentials
Web App (via Nginx)	http://localhost	—
Web App (direct)	http://localhost:5000	—
Prometheus	http://localhost:9090	—
Grafana	http://localhost:3000	admin / admin

Setting Up Grafana
Open http://localhost:3000 → log in with admin / admin
Connections → Data Sources → Add data source
Type: Prometheus
URL: http://prometheus:9090
Click Save & Test → should show "Datasource successful"
Dashboards → New → Import → paste ID 1860 → select your Prometheus source → Import
For a custom "is my app up?" panel:

Add visualization → Stat
Query: up{job="web-app"}
Thresholds: 1 = green, 0 = red
Chaos Engineering: Test the Self-Healing
# Kill the app
docker kill web-app

# Watch what happens:
#   1. Prometheus target goes red (~5s)
#   2. ServiceDown alert fires (~5s after that)
#   3. Docker restarts the container
#   4. Target goes green, alert resolves (~10s total)

# Verify:
curl -s 'http://localhost:9090/api/v1/query?query=up' | python3 -m json.tool
curl -s 'http://localhost:9090/api/v1/alerts' | python3 -m json.tool

# Or watch it live:
#   Prometheus UI → Status → Targets (red → green)
#   Prometheus UI → Alerts (firing → inactive)
#   Grafana → Explore → query `up{job="web-app"}`

Stress Test (CPU Spike)
# Trigger a 15-second CPU spike
curl http://localhost:5000/stress

# Watch CPU metrics in Grafana during the spike

Key Configuration
Health Check (docker-compose.yml)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 10s
  timeout: 5s
  retries: 3

Alert Rule (prometheus/alert.rules.yml)
groups:
  - name: self_healing_alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 5s
        labels:
          severity: critical
        annotations:
          description: "The web application container is down or unreachable."

Scrape Config (prometheus/prometheus.yml)
global:
  scrape_interval: 5s

rule_files:
  - "alert.rules.yml"

scrape_configs:
  - job_name: 'web-app'
    static_configs:
      - targets: ['web-app:5000']

Troubleshooting
Symptom	Cause	Fix
docker compose: command not found	Compose v2 plugin missing	sudo apt install docker-compose-plugin
address already in use	Port conflict	sudo lsof -i :PORT → kill or remap
Target health: down + unsupported Content-Type	Flask returns text/html	Use Response(..., content_type="text/plain; version=0.0.4")
found character that cannot start any token	Tab in YAML	sed -i 's/\t/ /g' file.yml
docker compose config fails	YAML syntax error	Fix indentation (spaces only)
Grafana can't reach Prometheus	Wrong URL in data source	Use http://prometheus:9090 (Docker DNS), not localhost

Stopping the Stack
docker compose down

Next Steps
[ ] Migrate to Azure Container Apps (managed, auto-scaling)
[ ] Add Alertmanager for Slack/email/PagerDuty notifications
[ ] Automate failure injection (cron-based chaos)
[ ] Add node_exporter for host-level metrics
[ ] Terraform module for infrastructure-as-code
[ ] Add /metrics with prometheus_flask_exporter for real request metrics
License
MIT


Drop that in as `README.md` in your project root. Want me to adjust the tone, add a GIF placeholder section, or tailor it for a specific audience (hiring managers, open-source contributors, etc.)?

Elaborate
How to add Alertmanager for external notifications?
How to containerize the Flask app?
How to configure Grafana dashboards?