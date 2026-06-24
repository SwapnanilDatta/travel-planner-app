# VoyAgent — AI Travel Planner

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat-square&logo=python)](https://python.org) [![Django](https://img.shields.io/badge/Django-6.0.6%2B-darkgreen?style=flat-square&logo=django)](https://djangoproject.com) [![FastAPI](https://img.shields.io/badge/FastAPI-blue?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com) [![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**VoyAgent** is an AI-powered travel planning platform for solo and group travelers. Describe where you want to go, and VoyAgent builds a full multi-day itinerary — complete with destination discovery, real-time collaboration, and visual search.

🌐 **Live demo:** [voyagent-mzei.onrender.com](https://voyagent-mzei.onrender.com)

---

## What it does

- **AI itinerary generation** — Multi-agent orchestration (CrewAI + LangChain) builds personalized day-by-day travel plans from a single prompt.
- **Group planning** — Shared itineraries and user profiles so everyone in the group stays on the same page.
- **Real-time chat** — Built-in WebSocket chat powered by Django Channels lets travelers coordinate without leaving the app.
- **Visual search** — A dedicated CLIP-based vision microservice classifies and embeds images so you can search destinations by photo.
- **Location-aware ranking** — Haversine distance scoring surfaces the most relevant nearby places.

---

## Architecture

VoyAgent is split into three deployable units:

```
┌─────────────────────────┐
│    Django Frontend      │  Sessions, UI, WebSocket chat, auth
│    (travel/)            │
└────────────┬────────────┘
             │ HTTP
    ┌────────┴────────┐         ┌──────────────────────┐
    │  FastAPI Core   │         │  FastAPI Vision       │
    │ (microservices/)│         │  (microservice2/)     │
    │                 │         │                       │
    │ • /generate     │         │ • /classify (CLIP)    │
    │ • Agent runner  │         │ • Image embeddings    │
    │ • Search utils  │         └──────────────────────┘
    └─────────────────┘
```

- **`travel/`** — Django app handling the frontend, authentication, templates, and Channels-based WebSocket connections. Includes `travel/ml.py` with image preprocessing and inference helpers shared with the vision microservice.
- **`microservices/`** — FastAPI service for itinerary generation, LLM agent orchestration, and search.
- **`microservice2/`** — Standalone FastAPI service for CLIP-based image classification and embedding. Ships with its own Dockerfile.

---

## Getting started

**Prerequisites:** Python 3.12+, Git, Docker (recommended)

### 1. Clone

```bash
git clone https://github.com/SwapnanilDatta/travel-planner-app.git
cd travel-planner-app
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in the values — see Environment variables below
```

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r microservices/requirements.txt
```

### 4. Run

Start the Django frontend:

```bash
cd travel
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Start the core microservice (new terminal):

```bash
cd microservices
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Optionally, start the vision microservice (new terminal):

```bash
cd microservice2
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

Open [http://localhost:8000](http://localhost:8000). API docs are available at `/docs` on each FastAPI service.

---

## Environment variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for local dev, `False` in production |
| `DATABASE_URL` | Postgres connection string |
| `MICROSERVICE_URL` | URL of the core FastAPI service |
| `MICROSERVICE2_URL` | URL of the vision microservice |
| `HF_API_TOKEN` | Hugging Face API token (for LLM/CLIP models) |
| `OPENCAGE_API_KEY` | Geocoding API key |
| `CLOUDINARY_URL` | Image storage (optional) |
| `REDIS_URL` | Redis for Channels and Celery |
| `CELERY_BROKER_URL` | Celery broker (usually same as `REDIS_URL`) |

Never commit real credentials. Use a secrets manager in production.

---

## API reference

### Core microservice (`localhost:8001`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/generate` | Generate a travel itinerary |
| `GET` | `/health` | Service health check |
| `GET` | `/docs` | Swagger UI |

### Vision microservice (`localhost:8002`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/classify` | Classify or embed an image via CLIP |
| `GET` | `/health` | Service health check |
| `GET` | `/docs` | Swagger UI |

See `microservices/models.py`, `microservice2/main.py`, and `travel/ml.py` for request/response schemas.

---

## Deployment

Each unit ships its own `Dockerfile`. For production:

- Use a managed **Postgres** database — remove the committed `travel/db.sqlite3` and add it to `.gitignore`.
- Run Uvicorn with multiple workers behind NGINX or a cloud load balancer.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Add service-to-service authentication between microservices (JWTs or mTLS).
- Expose `/health`, `/ready`, and `/metrics` endpoints; integrate Sentry and Prometheus.
- Rotate secrets regularly via a secret manager.

---

## Troubleshooting

**WebSocket errors** — Verify Django Channels is configured and you're running an ASGI server (Daphne or Uvicorn with ASGI mode).

**Agent timeouts** — Check that `HF_API_TOKEN` (or your LLM provider key) is valid and that outbound network access is allowed from the microservice host.

**Database errors** — Ensure `DATABASE_URL` points to a running Postgres instance and `migrate` has been applied.

**Image classification issues** — Confirm the CLIP model artifacts are accessible to `microservice2` and that the preprocessing in `travel/ml.py` matches the model's expected input format.

---

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Run linters locally: `black .` and `flake8`
4. Open a pull request with a clear description of what changed and why

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Author

**Swapnanil Datta** — [github.com/SwapnanilDatta](https://github.com/SwapnanilDatta)

Built with Django, FastAPI, CrewAI, LangChain, and Django Channels.
