# UPTC EcoEnergy

Energy monitoring and optimization platform for the four campuses of the
Universidad Pedagógica y Tecnológica de Colombia (Tunja, Duitama, Sogamoso and
Chiquinquirá). Built during the HackDay IAMinds hackathon.

The platform ingests 7+ years of hourly consumption data (275,000+ records)
and provides:

- Dashboards with KPIs, consumption trends and sector breakdowns per campus
- Energy and CO2 predictions using a two-stage ML pipeline
- Anomaly detection over historical baselines
- Rule-based and AI-generated saving recommendations
- SHAP values to explain what drives each prediction
- An optional Telegram bot for alerts and quick queries

## Quick start

Requires Docker and Docker Compose.

```bash
git clone https://github.com/NicolasV7/uptc-ecoenergy.git
cd uptc-ecoenergy
docker compose up -d --build
```

No `.env` needed: everything has defaults. Once up:

| Service | URL |
|---|---|
| Frontend | http://localhost:8080 |
| API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs (with `DEBUG=true`) |

To enable the Telegram bot, set `TELEGRAM_BOT_TOKEN` in `.env` and run
`docker compose --profile with-bot up -d --build`.

## Architecture

```
users ──> frontend (nginx + React SPA) :8080
              │  /api/ proxied by nginx
              v
          backend (FastAPI + ML models + SQLite) :8000
              ^
              │
          telegram bot (optional)
```

React 18 + TypeScript + Vite on the front (Tailwind, shadcn/ui, Recharts,
Leaflet for campus maps). FastAPI with async SQLAlchemy on the back, SQLite
for the time series, scikit-learn/LightGBM for the models. An OpenAI key is
optional: with it you get the chat assistant and smarter recommendations,
without it the AI features fall back to local responses.

## ML pipeline

Two-stage prediction:

1. A LightGBM regressor predicts CO2 emissions from 33 temporal and
   contextual features.
2. A Ridge regression predicts energy consumption (kWh) using 35 features,
   including the predicted CO2 from stage 1.

Anomaly detection runs Isolation Forest against historical baselines with
configurable sensitivity. SHAP values and confidence scores are exposed
through the API for explainability. Model artifacts live in `models/` and are
loaded at startup.

## Project structure

```
uptc-ecoenergy/
├── backend/          # FastAPI app: endpoints, ML inference, ORM, services
├── frontend/         # React SPA + nginx config for production
├── telegram-bot/     # Optional bot (python-telegram-bot)
├── models/           # Trained model artifacts
├── datasets/         # Source CSVs (275K+ records)
└── docker-compose.yml
```

## Configuration

All variables are optional; see [`.env.example`](.env.example) for the full
list. The relevant ones:

| Variable | Purpose |
|---|---|
| `DEBUG` | Swagger docs, verbose logging, auto DB init (default `true`) |
| `OPENAI_API_KEY` | Enables AI chat and recommendations |
| `TELEGRAM_BOT_TOKEN` | Enables the bot (get one from @BotFather) |
| `DATABASE_URL` | Defaults to a SQLite file in a Docker volume |

## API

Base URL: `http://localhost:8000/api/v1`. Main endpoint groups:

- `analytics/`: dashboard KPIs, sector breakdowns, hourly patterns,
  correlations, academic periods
- `predictions/`: single and batch predictions, model metrics
- `anomalies/`: list, detect, update status
- `recommendations/`: rule-based and AI generation per campus
- `optimization/`: saving opportunities, projections, sustainability metrics,
  Pareto analysis
- `explainability/`: SHAP values per variable, confidence scores
- `chat`, `sedes`, `health`

Full interactive reference in Swagger at `/docs`.

## Local development

Backend:

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_sqlite.py                     # loads CSV data
uvicorn app.main:app --reload --port 8000
```

Frontend (set `VITE_API_URL=http://localhost:8000` in `frontend/.env`):

```bash
cd frontend
npm install
npm run dev
```

## License

MIT. Built by the HackDay IAMinds team.
