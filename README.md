# VoyAgent — AI Travel Planner

VoyAgent is an AI-powered travel planning platform for solo and group travellers. Give a destination and preferences, and the system produces a day-by-day itinerary, cost estimate, and image/text embeddings to power visual search and recommendations.

[Live demo (unchanged)](https://voyagent-mzei.onrender.com)

---

## What changed

This README replaces an older architecture description. Two components and their integration have been updated:

- The itinerary generator (microservices/) now runs as an agentic FastAPI service that creates tasks and completes them asynchronously. It exposes polling endpoints and supports an optional webhook to receive results when generation finishes.
- The budget predictor remains a standalone FastAPI microservice (see budget_predictor/) but is described separately below; use its README for model and training details.

The public URLs and repository layout are unchanged.

---

## Stack
- Language(s): Python (backend), HTML/CSS (frontend templates)
- Frameworks: Django (frontend + auth + WebSocket chat), FastAPI (microservices)
- Notable libraries: Pydantic, SentenceTransformers (CLIP), XGBoost (budget model), Django Channels

## How it's organized

```
travel/                 Django frontend (templates, auth, Channels WebSockets)
microservices/          Agentic itinerary FastAPI service (async tasks)
microservice2/          CLIP-based embedding service (text/image -> embeddings)
budget_predictor/       Budget estimation FastAPI service + model artifacts
README.md               This file (updated)
requirements.txt        Root Python deps
pyproject.toml          Project metadata
```

How it fits together: The Django frontend (travel/) is the user-facing app. It calls the itinerary microservice to request a travel plan; the microservice runs generation asynchronously (using LLM orchestration in llm_wrapper.py) and either sends a webhook to a callback URL or returns the result for the frontend to poll. The vision microservice (microservice2/) provides CLIP embeddings for images or text; the budget_predictor service returns ML-driven cost estimates for a requested trip.

---

## Updated architecture (short)

- Frontend (Django) — handles sessions, user accounts, templates and Channels-based realtime chat.
- Itinerary microservice (microservices/) — POST /plan-trip to start a job, POST /regenerate-day to regenerate a specific day, GET /task/{task_id} to poll results. Jobs run in background tasks and store results in an in-memory TASK_RESULTS dict (suitable for development; use persistent storage/queue in production). Supports sending a JSON webhook payload to a provided webhook_url once the job completes.
- Vision microservice (microservice2/) — POST /embed accepts either `text` or `image_b64` and returns a CLIP embedding.
- Budget predictor (budget_predictor/) — FastAPI endpoint (typically POST /predict) that returns a cost estimate using a serialized model (see budget_predictor/README.md for data and model details).

---

## API reference (current)

### Itinerary microservice (run from microservices/)
- POST /plan-trip
  - Starts an asynchronous itinerary generation task. Request should follow the TripRequest schema used by microservices/models.py. Returns {"task_id": "...", "status": "processing", ...}.
  - Optional: include `webhook_url` in your payload to receive a POST callback when the job completes.

- POST /regenerate-day
  - Start an async task to regenerate a single day's content. Returns a task_id to poll.

- GET /task/{task_id}
  - Poll this endpoint to retrieve status and results. When completed, the service stores the response under the task_id and returns the generated content or an error.

Notes: The service currently keeps results in memory (TASK_RESULTS) — replace with Redis, database, or a message queue (Celery/RQ) for production.

### Vision microservice (run from microservice2/)
- POST /embed
  - Payload: {"text": "..."} or {"image_b64": "..."}
  - Returns: {"embedding": [float, float, ...]}

### Budget predictor (see budget_predictor/README.md)
- POST /predict
  - Payload example:
    {
      "destination": "Goa",
      "month": 12,
      "duration_days": 5,
      "group_size": 2,
      "pace": "Moderate"
    }
  - Returns an estimated trip cost and (optionally) per-person breakdown.

---

## Getting started (short path)

Prerequisites: Python 3.12+, Git, Docker (optional)

1) Clone

```bash
git clone https://github.com/SwapnanilDatta/travel-planner-app.git
cd travel-planner-app
```

2) Configure environment

```bash
cp .env.example .env
# Edit .env with your keys and database URL
```

3) Install Python dependencies (suggested inside a venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# If running microservices separately:
pip install -r microservices/requirements.txt
pip install -r microservice2/requirements.txt
```

4) Run services (development)

```bash
# Django frontend
cd travel
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# Core itinerary microservice (new terminal)
cd ../microservices
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Vision microservice (new terminal)
cd ../microservice2
uvicorn main:app --reload --host 0.0.0.0 --port 8002

# Budget predictor (if running locally)
# cd ../budget_predictor
# uvicorn main:app --reload --host 0.0.0.0 --port 7860
```

Open http://localhost:8000 for the frontend. Each FastAPI service exposes /docs for OpenAPI documentation.

---

## Environment variables (highlight)
- SECRET_KEY — Django secret
- DEBUG — True for dev
- DATABASE_URL — Postgres connection string
- MICROSERVICE_URL — core itinerary service base URL
- MICROSERVICE2_URL — vision/embedding service URL
- HF_API_TOKEN — Hugging Face token (for model access)
- OPENCAGE_API_KEY — Geocoding API key
- CLOUDINARY_URL — optional image storage
- REDIS_URL, CELERY_BROKER_URL — recommended for production background tasks

---

## Production notes & TODO
- Replace in-memory TASK_RESULTS with durable storage (Redis/DB) and use a proper queue (Celery/RQ) for background tasks.
- Add authenticated service-to-service requests (JWT or mTLS) before exposing microservice endpoints.
- Add readiness/metrics endpoints and configure logging/monitoring (Sentry/Prometheus).
- Containerize each service and provide a docker-compose or Kubernetes manifests for deployment.

---

## Contributing
1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Run linters: `black .` and `flake8`
4. Open a PR describing the change

---

## License
MIT — see [LICENSE](LICENSE)

---

## Author
**Swapnanil Datta** — https://github.com/SwapnanilDatta

If you'd like, I can also:
- update the budget_predictor/README to match any architecture changes you have in mind,
- add example request payloads (TripRequest schema) or a sample webhook consumer,
- generate docker-compose for local integration testing.
