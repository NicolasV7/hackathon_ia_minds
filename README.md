<div align="center">

# UPTC EcoEnergy

### AI-Powered Energy Monitoring & Optimization Platform

**Real-time energy analytics, ML-based predictions, and actionable recommendations for the Universidad Pedagogica y Tecnologica de Colombia (UPTC).**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Quick Start](#-quick-start) &bull; [Architecture](#-architecture) &bull; [API Reference](#-api-reference) &bull; [Local Development](#-local-development) &bull; [Contributing](#-contributing)

</div>

---

## About

UPTC EcoEnergy is a full-stack platform that monitors and optimizes energy consumption across 4 university campuses. Built during the **HackDay IAMinds** hackathon, it combines 7+ years of historical data (275,000+ hourly records) with machine learning models to deliver:

- **Real-time dashboards** with KPIs, consumption trends, and sector breakdowns
- **ML predictions** for energy and CO2 emissions using LightGBM and Ridge models
- **Anomaly detection** with Isolation Forest to flag unusual consumption patterns
- **AI-powered recommendations** via OpenAI for actionable energy savings
- **SHAP explainability** to understand what drives model predictions
- **Telegram bot** for on-the-go access to analytics and alerts

### Campus Coverage

| Campus | Students | Location |
|---|---|---|
| Tunja (Main) | ~18,000 | Boyaca, Colombia |
| Duitama | ~5,500 | Boyaca, Colombia |
| Sogamoso | ~6,000 | Boyaca, Colombia |
| Chiquinquira | ~2,000 | Boyaca, Colombia |

---

## Quick Start

> **Prerequisites:** [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### 1. Clone & Run

```bash
git clone https://github.com/NicolasV7/hackathon_ia_minds.git
cd hackathon_ia_minds
docker compose up -d --build
```

That's it. No `.env` file needed -- all defaults are built in.

### 2. (Optional) Customize with `.env`

```bash
cp .env.example .env   # edit values you want to change
docker compose up -d --build
```

### 3. Access the App

| Service | URL | Description |
|---|---|---|
| **Frontend** | [http://localhost:8080](http://localhost:8080) | React dashboard |
| **API** | [http://localhost:8000](http://localhost:8000) | FastAPI backend |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI (when `DEBUG=true`) |
| **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | Service status |

### Optional: Enable the Telegram Bot

```bash
# Set your bot token in .env first, then:
docker compose --profile with-bot up -d --build
```

### Useful Commands

```bash
# View logs
docker compose logs -f backend

# Restart a single service
docker compose restart backend

# Stop everything
docker compose down

# Stop & remove data (reset database)
docker compose down -v
```

---

## Architecture

```
                    +-------------------+
                    |   Users / Browser |
                    +--------+----------+
                             |
                    +--------v----------+
                    |  Frontend (nginx) |  :8080
                    |  React + Vite     |
                    +--------+----------+
                             |
                    /api/ proxy (nginx)
                             |
                    +--------v----------+
                    |  Backend (FastAPI) |  :8000
                    |  + ML Models      |
                    |  + SQLite DB      |
                    +--------+----------+
                             |
                    +--------v----------+
                    |  Telegram Bot     |  (optional)
                    |  python-telegram  |
                    +-------------------+
```

### Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18, TypeScript, Vite | Single-page application |
| **UI** | Tailwind CSS, shadcn/ui, Recharts | Design system & data visualization |
| **Maps** | Leaflet, MapLibre GL | Campus geospatial visualization |
| **Backend** | FastAPI, SQLAlchemy (async) | REST API & business logic |
| **ML** | scikit-learn, XGBoost, LightGBM | Prediction & anomaly detection |
| **Database** | SQLite (aiosqlite) | Time-series consumption data |
| **AI** | OpenAI GPT (optional) | Chat assistant & smart recommendations |
| **Bot** | python-telegram-bot | Telegram integration |
| **Infra** | Docker, nginx | Containerization & reverse proxy |

---

## Project Structure

```
hackathon_ia_minds/
|
+-- backend/                      # FastAPI backend
|   +-- app/
|   |   +-- main.py               # Application entry point
|   |   +-- api/v1/endpoints/     # REST endpoints (11 modules)
|   |   +-- core/                 # Config, database, dependencies
|   |   +-- ml/                   # ML inference, features, anomaly detection
|   |   +-- models/               # SQLAlchemy ORM models
|   |   +-- schemas/              # Pydantic request/response schemas
|   |   +-- repositories/         # Data access layer
|   |   +-- services/             # Business logic layer
|   +-- ml_models/                # Serialized models (.joblib)
|   +-- scripts/                  # DB init & data loading
|   +-- Dockerfile
|   +-- requirements.txt
|
+-- frontend/                     # React SPA
|   +-- src/
|   |   +-- pages/                # Route pages (dashboard, analytics, etc.)
|   |   +-- components/           # UI components + shadcn/ui
|   |   +-- services/api.ts       # API client with fallback mock data
|   |   +-- hooks/                # Custom React hooks
|   +-- nginx.conf                # Production reverse proxy config
|   +-- Dockerfile
|   +-- package.json
|
+-- telegram-bot/                 # Telegram bot (optional)
|   +-- app.py                    # Bot entry point
|   +-- Dockerfile
|   +-- requirements.txt
|
+-- models/                       # Trained ML model artifacts (.pkl)
+-- datasets/                     # Source CSV data (275K+ records)
+-- docker-compose.yml            # Service orchestration
+-- .env.example                  # Environment variable template
```

---

## Environment Variables

All configuration is done through a single `.env` file. See [`.env.example`](.env.example) for the full template with descriptions.

**All variables are optional.** The app works out of the box with zero configuration.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///app/data/uptc_energy.db` | Database connection string |
| `DEBUG` | `true` | Enables Swagger docs, verbose logging, auto DB init |
| `CORS_ORIGINS_STR` | `http://localhost:3000,http://localhost:8080` | Allowed CORS origins (comma-separated) |
| `OPENAI_API_KEY` | _(empty)_ | Enables AI chat & smart recommendations. Without it, AI features return local fallback responses |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use (e.g., `gpt-4o-mini`, `gpt-4o`) |
| `VITE_API_URL` | _(empty)_ | Frontend API URL. Leave empty for Docker (nginx proxy handles it) |
| `TELEGRAM_BOT_TOKEN` | _(empty)_ | Telegram bot token from [@BotFather](https://t.me/BotFather). Without it, the bot stays idle |

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics/dashboard/{sede}` | Dashboard KPIs by campus |
| `GET` | `/analytics/consumption/sectors/{sede}` | Consumption breakdown by sector |
| `GET` | `/analytics/patterns/hourly/{sede}` | Hourly consumption patterns |
| `GET` | `/analytics/correlations/{sede}` | Variable correlations matrix |
| `GET` | `/analytics/academic-periods` | Consumption by academic period |

### Predictions
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predictions/` | Create a new prediction |
| `POST` | `/predictions/batch` | Batch prediction (multi-hour horizon) |
| `GET` | `/predictions/sede/{sede}` | Get predictions by campus |
| `GET` | `/models/metrics` | ML model performance metrics |

### Anomalies
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/anomalies/` | List detected anomalies |
| `POST` | `/anomalies/detect` | Run anomaly detection |
| `PATCH` | `/anomalies/{id}/status` | Update anomaly status |

### Recommendations
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/recommendations/sede/{sede}` | Get recommendations by campus |
| `POST` | `/recommendations/generate` | Generate rule-based recommendations |
| `POST` | `/recommendations/ai-generate` | Generate AI-powered recommendations |

### Optimization
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/optimization/opportunities` | Energy saving opportunities |
| `GET` | `/optimization/savings-projection` | Projected savings waterfall |
| `GET` | `/optimization/sustainability` | Green metrics (trees saved, CO2 reduced) |
| `GET` | `/optimization/pareto` | Pareto analysis of waste sources |

### Explainability
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/explainability/shap/{variable}` | SHAP feature importance values |
| `GET` | `/explainability/confidence` | Model confidence scores |

### Chat & Utilities
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send message to AI assistant |
| `GET` | `/sedes` | List all campus information |
| `GET` | `/health` | Health check (root level) |

> Interactive documentation available at [http://localhost:8000/docs](http://localhost:8000/docs) when `DEBUG=true`.

---

## ML Models

The platform uses a **two-stage prediction pipeline**:

### Stage 1: CO2 Prediction
- **Algorithm:** LightGBM Regressor
- **Features:** 33 temporal & contextual features
- **Output:** Predicted CO2 emissions (kg)

### Stage 2: Energy Prediction
- **Algorithm:** Ridge Regression
- **Features:** 35 features (including predicted CO2 from Stage 1)
- **Output:** Predicted energy consumption (kWh)

### Anomaly Detection
- **Algorithm:** Isolation Forest
- **Input:** Consumption features vs historical baselines
- **Sensitivity:** Configurable (low / medium / high)

### Explainability
- **SHAP values** for feature importance visualization
- **Confidence scores** for prediction reliability

Model artifacts are stored in `models/` as `.pkl` files and loaded at application startup.

---

## Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database (loads CSV data)
python scripts/init_sqlite.py

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (http://localhost:8080)
npm run dev
```

> Set `VITE_API_URL=http://localhost:8000` in `frontend/.env` for local development so the frontend can reach the backend directly.

### Telegram Bot

```bash
cd telegram-bot

pip install -r requirements.txt

# Set required environment variables
export TELEGRAM_BOT_TOKEN=your_token_here
export OPENAI_API_KEY=your_key_here       # optional
export API_BASE_URL=http://localhost:8000/api/v1

python app.py
```

---

## Docker Details

The project uses **multi-stage Docker builds** for optimized production images:

| Service | Base Image | Final Size | Port |
|---|---|---|---|
| Backend | `python:3.12-slim` | ~800MB (includes ML libs) | 8000 |
| Frontend | `nginx:alpine` | ~30MB | 80 (mapped to 8080) |
| Telegram Bot | `python:3.11-slim` | ~200MB | - |

### How It Works

1. **Backend container** starts, loads ML models from `/app/models`, and initializes the SQLite database from CSV data in the background
2. **Frontend container** waits for backend to be healthy, then serves the React SPA via nginx, which also proxies `/api/` requests to the backend
3. **Telegram bot** (optional, via `--profile with-bot`) connects to the backend API and Telegram servers

### Data Persistence

- SQLite database is stored in a Docker named volume (`uptc-sqlite-data`)
- CSV datasets are mounted read-only from `./datasets`
- To reset the database: `docker compose down -v && docker compose up -d`

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with care by the HackDay IAMinds Team**

FastAPI &bull; React &bull; scikit-learn &bull; LightGBM &bull; Docker

</div>
