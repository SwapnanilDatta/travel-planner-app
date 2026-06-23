# VoyAgent — Travel Planner App

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat-square&logo=python)](https://python.org) [![Django](https://img.shields.io/badge/Django-6.0.6%2B-darkgreen?style=flat-square&logo=django)](https://djangoproject.com) [![FastAPI](https://img.shields.io/badge/FastAPI-blue?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com) [![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

Live deployment: https://voyagent-mzei.onrender.com

A modern, AI-assisted travel planning platform that helps groups and solo travelers discover destinations, build multi-day itineraries, and collaborate in real time. The frontend is a Django web app with realtime chat support; the backend is split into FastAPI microservices that orchestrate the AI agents, search, and itinerary generation.

Key principles: modular microservices, LLM & agent-based planning, realtime collaboration, and developer-friendly local development.

---

## Quick links

- Live site: https://voyagent-mzei.onrender.com
- API docs (FastAPI /microservices): visit your FastAPI service /docs when running locally

---

## Features

- AI-driven itinerary generation using multi-agent orchestration
- Group planning with shared itineraries and user profiles
- Location search and geospatial ranking (Haversine distances)
- Real-time chat powered by Django Channels (WebSockets)
- Separate FastAPI microservices for AI tasks and search
- Docker-ready services and example environment configuration

---

## Architecture overview

- `travel/` — Django monolith that serves the frontend, authentication, templates, and Channels-based realtime features.
- `microservices/` — FastAPI application that exposes endpoints for generating itineraries, running AI agents, and search utilities.
- `microservice2/` — Additional microservice with its own Dockerfile (kept as a separate deployable unit).

How it fits together: the Django frontend handles user sessions, UI, and websocket connections; when the app needs an itinerary or heavy LLM work it calls the FastAPI microservice(s) which run the agent orchestration and return structured results. Each microservice exposes OpenAPI docs and can be deployed independently.

---

## Screenshots / Demo

Open the live deployment to try the app: https://voyagent-mzei.onrender.com

---

## Getting started — Local development (short path)

Prerequisites:

- Python 3.12+
- Git
- Docker & docker-compose (recommended for local dev with Postgres/Redis)

1. Clone the repo

```bash
git clone https://github.com/SwapnanilDatta/travel-planner-app.git
cd travel-planner-app
```

2. Copy environment variables

```bash
cp .env.example .env
# Open .env and fill real values (or configure secrets in your platform)
```

3. Recommended: run with Docker Compose (example)

> If you want, I can add a docker-compose.yml that wires Django + Postgres + Redis + microservices. For now the easy (no-docker) dev flow is below.

4. Install Python deps (venv recommended)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r microservices/requirements.txt
```

5. Run Django migrations and start services

```bash
cd travel
python manage.py migrate
python manage.py runserver 0.0.0.0:8000        # development server for the frontend
```

In another terminal, run the FastAPI microservice:

```bash
cd microservices
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Visit http://localhost:8000 to load the frontend and try the flows. The FastAPI docs will be available at http://localhost:8001/docs.

---

## Environment variables

A `.env.example` is included at the repository root. Important variables you should set before running:

- APP_ENV, DEBUG, SECRET_KEY
- DATABASE_URL (use Postgres in production)
- MICROSERVICE_URL, MICROSERVICE2_URL
- HF_API_TOKEN, OPENCAGE_API_KEY, CLOUDINARY_URL (if used)
- REDIS_URL and CELERY_BROKER_URL (if you run background workers)

Never commit sensitive values to source control. Use a secret manager or your cloud provider's secret store in production.

---

## Docker & Deployment notes

- There are Dockerfiles in the repository root and `microservice2/`. Use these to build container images for deployments.
- For production deployments:
  - Use a managed database (Postgres), not SQLite
  - Run Uvicorn with multiple workers behind an HTTP proxy (NGINX / cloud load balancer)
  - Set DEBUG=False and configure ALLOWED_HOSTS
  - Use HTTPS and rotate secrets via a secret manager
  - Add liveness/readiness endpoints, and /metrics for Prometheus scraping

If you'd like, I can add a CI workflow that builds and pushes Docker images to Docker Hub / GitHub Container Registry and a `docker-compose.yml` for local development.

---

## API Endpoints (overview)

- FastAPI microservice (default when running locally on port 8001):
  - `POST /generate` — trigger itinerary generation (body depends on the microservice models)
  - `GET /health` — service health
  - `GET /docs` — OpenAPI / Swagger UI

- Django frontend: serves pages, websocket endpoints for chat, and integrates with the microservices via configured environment MICROSERVICE_URLs.

See `microservices/models.py` and `microservices/main.py` for the exact request/response shapes.

---

## Production checklist

1. Remove committed SQLite DB (`travel/db.sqlite3`) from the repo and add it to `.gitignore`.
2. Set DEBUG=False and APP_ENV=production.
3. Use Postgres (managed) and run migrations there.
4. Add service-to-service authentication (JWTs, mTLS) between microservices.
5. Add monitoring (Prometheus) and error reporting (Sentry).
6. Add CI: tests, linters, dependency scanning, container image builds.
7. Add automated backups for DB and rotate secrets regularly.

---

## Testing

- Unit tests / API tests (if present) can be run with pytest. I can add a test suite and CI pipeline if you'd like.

---

## Contributing

Contributions are welcome. Typical flow:

1. Fork the repository
2. Create a branch: `git checkout -b feat/awesome`
3. Make changes, run linters/tests locally
4. Open a PR with a clear description

Please run linters (black, flake8) and keep changes focused and well-documented.

---

## Troubleshooting

- If websockets fail, ensure Channels and Daphne (or ASGI server) are configured and running.
- If AI agents time out, verify that HF_API_TOKEN (or LLM provider keys) are valid and that network egress is allowed.
- For DB errors, ensure DATABASE_URL points to a reachable Postgres instance and migrations have been applied.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Author

Swapnanil Datta — https://github.com/SwapnanilDatta

---

## Acknowledgments

- Django, FastAPI
- CrewAI and LangChain for agent & LLM orchestration

---

If you'd like, I can further:
- Add a polished `docker-compose.yml` for local development
- Add a CI workflow to run tests, linters, and build container images
- Remove the committed SQLite DB from HEAD (non-destructive) and add `.gitignore` update

Tell me which of the above you'd like me to do next and I’ll proceed.