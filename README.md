# 🌍 UPTC EcoEnergy - Sistema de Monitoreo y Optimización Energética

<div align="center">

**Plataforma inteligente para monitoreo, análisis y optimización del consumo energético y de agua en la Universidad Pedagógica y Tecnológica de Colombia (UPTC).**

[Características](#características) • [Instalación](#instalación) • [Uso](#uso) • [Estructura](#estructura) • [API](#api) • [Contribuir](#contribuir)

</div>

---

## 📋 Descripción

UPTC EcoEnergy es un sistema integral de monitoreo energético que proporciona:

- 📊 **Análisis detallado** del consumo de energía y agua por sede y sector
- 🤖 **Predicciones ML** basadas en historial de 7+ años de datos (2018-2025)
- 🚨 **Detección de anomalías** en tiempo real con IA
- 💡 **Recomendaciones automáticas** de ahorro energético
- 🌱 **Métricas de sostenibilidad** (árboles salvados, CO₂ reducido, etc.)
- 💬 **Chatbot asistente** con IA para consultas sobre eficiencia

### Cobertura
- **4 sedes**: Tunja (principal), Duitama, Sogamoso, Chiquinquirá
- **5 sectores**: Comedores, Salones, Laboratorios, Auditorios, Oficinas
- **Datos históricos**: 275,000+ registros horarios (2018-2025)
- **Granularidad**: Horaria en tiempo real

---

## ✨ Características Principales

### 🔍 Dashboard Analítico
- **Distribución de consumo** por sector y sede en tiempo real
- **Patrones horarios** de uso de energía durante el día
- **Correlaciones** entre variables (energía, agua, temperatura)
- **Análisis de Pareto** para identificar las mayores fuentes de desperdicio
- **Comparativas** entre períodos académicos y vacaciones

### 🧠 Machine Learning
- **XGBoost & Scikit-learn** para predicción de consumo
- **Modelos entrenados** con 7 años de historial (18,000+ estudiantes en Tunja)
- **Precisión de predicción**: R² > 0.85 en validación
- **Detección de anomalías** con Isolation Forest
- **SHAP values** para explicabilidad de modelos

### 💾 Base de Datos
- **SQLite optimizado** para consultas de series de tiempo
- **Índices compuestos** para filtrado rápido por sede + fecha
- **Columnas normalizadas** para agua (litros), energía (kWh), CO₂ (kg)
- **Metadatos temporales**: hora, día, período académico, festivos

### 🔐 API REST
- **FastAPI** con documentación Swagger automática
- **Endpoints** para analytics, predicciones, recomendaciones, anomalías
- **Autenticación** preparada para OAuth2
- **Rate limiting** y validación de entrada

### 🎨 Frontend Moderno
- **React + TypeScript** para máxima confiabilidad
- **Vite** para desarrollo rápido (HMR)
- **Tailwind CSS + shadcn/ui** para UI profesional
- **Recharts** para visualizaciones interactivas
- **Responsive design** (mobile, tablet, desktop)

---

## 🚀 Quick Start

### Requisitos Previos
- **Python 3.12+** (backend)
- **Node.js 18+** (frontend)
- **Docker & Docker Compose** (opcional)
- **Git**

### Instalación Local

#### 1️⃣ Clonar repositorio
```bash
git clone https://github.com/yourusername/hackathon_ia_minds.git
cd hackathon_ia_minds
```

#### 2️⃣ Configurar Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
# o con Poetry:
poetry install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con valores locales

# Inicializar base de datos
python scripts/init_sqlite.py

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3️⃣ Configurar Frontend
```bash
cd frontend

# Instalar dependencias
npm install
# o con bun:
bun install

# Iniciar servidor de desarrollo
npm run dev
# Accesible en: http://localhost:5173
```


## 📁 Estructura del Proyecto

```
hackathon_ia_minds/
├── backend/                          # 🔷 FastAPI Backend
│   ├── app/
│   │   ├── main.py                  # Punto de entrada
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── analytics.py      # Dashboard KPIs
│   │   │       │   ├── predictions.py    # Predicciones ML
│   │   │       │   ├── anomalies.py      # Detección de anomalías
│   │   │       │   ├── recommendations.py # Recomendaciones IA
│   │   │       │   ├── optimization.py   # Oportunidades de ahorro
│   │   │       │   └── chat.py           # Chatbot asistente
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py            # Configuración (env vars)
│   │   │   ├── database.py          # Conexión SQLite + SQLAlchemy
│   │   │   ├── dependencies.py      # inyecciones de dependencia
│   │   │   └── websocket.py         # WebSocket para updates
│   │   ├── models/                  # Modelos SQLAlchemy ORM
│   │   │   ├── consumption.py       # Registros de consumo
│   │   │   ├── prediction.py        # Predicciones guardadas
│   │   │   ├── anomaly.py           # Anomalías detectadas
│   │   │   └── recommendation.py    # Recomendaciones
│   │   ├── schemas/                 # Esquemas Pydantic
│   │   ├── repositories/            # Patrón Repository
│   │   ├── services/                # Lógica de negocio
│   │   │   ├── analytics_service.py
│   │   │   ├── prediction_service.py
│   │   │   └── ml_service.py
│   │   └── ml/                      # Modelos & ML utilities
│   │       ├── inference.py         # Cargar y usar modelos
│   │       ├── models/              # Modelos XGBoost guardados
│   │       └── features.py          # Engineering de features
│   ├── scripts/
│   │   └── init_sqlite.py           # Inicializar BD
│   ├── ml_models/                   # Modelos entrenados (.joblib)
│   │   ├── energy_predictor.joblib
│   │   └── anomaly_detector.joblib
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                         # ⚛️ React + TypeScript
│   ├── src/
│   │   ├── main.tsx                 # Entry point
│   │   ├── App.tsx                  # Root component
│   │   ├── pages/
│   │   │   ├── Index.tsx            # Landing page
│   │   │   ├── LandingPage.tsx      # Presentación
│   │   │   ├── dashboard/
│   │   │   │   ├── AnalyticsPage.tsx    # Dashboard principal
│   │   │   │   ├── PredictionsPage.tsx  # Predicciones
│   │   │   │   ├── AnomaliesPage.tsx    # Alertas de anomalías
│   │   │   │   └── RecommendationsPage.tsx
│   │   │   └── NotFound.tsx
│   │   ├── components/
│   │   │   ├── Chatbot.tsx          # Chat asistente
│   │   │   ├── NavLink.tsx
│   │   │   ├── dashboard/           # Componentes del dashboard
│   │   │   ├── landing/             # Componentes de inicio
│   │   │   └── ui/                  # shadcn/ui components
│   │   ├── services/
│   │   │   └── api.ts               # Cliente HTTP a backend
│   │   ├── hooks/                   # Custom React hooks
│   │   └── lib/
│   │       └── utils.ts
│   ├── public/                      # Assets estáticos
│   ├── Dockerfile
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── package.json
│   └── index.html
│
├── datasets/            # 📊 Dataset original
│   ├── consumos_uptc.csv            # 275k registros horarios
│   ├── sedes_uptc.csv               # Info de 4 sedes
│   └── CODEBOOK_UPTC.md             # Diccionario de datos
│
├── models/                        # 📋 Documentación de modelos
│   ├── documentacion_backend.json
│   └── modelo_energia_B2_info.json
│
├── telegram_bot/                     # 🤖 Bot Telegram (opcional)
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml               # Orquestación de servicios
├── .env.example                     # Template de variables
└── README.md                        # Este archivo
```

---

## 🔌 API Endpoints

### Dashboard URL
```
http://77.42.26.173:8080/
```

### 📊 Analytics
```
GET    /analytics/dashboard/{sede}              # KPIs por sede
GET    /analytics/consumption/sectors/{sede}    # Desglose por sector
GET    /analytics/patterns/hourly/{sede}        # Patrones horarios
GET    /analytics/correlations/{sede}           # Correlaciones
GET    /analytics/academic-periods              # Por período escolar
```

### 🔮 Predicciones
```
POST   /predictions/                            # Crear predicción
GET    /predictions/?sede=tunja                 # Listar predicciones
GET    /predictions/{id}                        # Detalle predicción
GET    /models/metrics                          # Métricas de modelos
```

### 🚨 Anomalías
```
GET    /anomalies/                              # Listar anomalías activas
POST   /anomalies/                              # Reportar anomalía
PATCH  /anomalies/{id}/status                   # Cambiar estado
```

### 💡 Recomendaciones
```
GET    /recommendations/sede/{sede}             # Por sede
POST   /recommendations/generate                # Generar nuevas
PATCH  /recommendations/{id}/status             # Cambiar estado
POST   /recommendations/ai-generate             # Con IA (GPT-4)
```

### 🌱 Optimización
```
GET    /optimization/opportunities              # Oportunidades de ahorro
GET    /optimization/savings-projection         # Proyección de ahorros
GET    /optimization/sustainability             # Métricas verdes
GET    /optimization/pareto                     # Análisis Pareto
```

### 💬 Chat IA
```
POST   /chat                                    # Enviar mensaje
```

### ✅ Health
```
GET    /health                                  # Estado del servidor
```

### 📚 Documentación interactiva
```
http://localhost:8000/docs                      # Swagger UI
http://localhost:8000/redoc                     # ReDoc
```

## 🤖 Modelos ML

### 🎯 Predictor de Energía
- **Algoritmo**: XGBoost Regressor
- **Features**: 40+ features de contexto temporal, ocupación, historial
- **Precisión**: R² = 0.87, RMSE = 2.3 kWh
- **Horizonte**: Predicción 24h a 7 días
- **Reentrenamiento**: Automático cada 7 días

### 🚨 Detector de Anomalías
- **Algoritmo**: Isolation Forest
- **Entrada**: Valor actual vs. histórico
- **Sensibilidad**: Configurable (bajo/medio/alto)
- **Latencia**: <100ms

### 📊 Recomendador IA
- **Motor**: GPT-4 + Context Engineering
- **Entrada**: Métricas de consumo + Oportunidades detectadas
- **Salida**: 3-5 recomendaciones priorizadas
- **ROI estimado**: Calculado por oportunidad

---

## 📝 Licencia

Este proyecto está licenciado bajo la licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

---

## 👥 Autores & Créditos

**HackDay IAMinds Team** - Equipo de desarrollo para Hackathon de IA y Eficiencia Energética

### Stack Principal
- **Backend**: FastAPI, SQLAlchemy, XGBoost
- **Frontend**: React, TypeScript, Tailwind CSS
- **ML**: scikit-learn, pandas, numpy
- **DB**: SQLite (dev), PostgreSQL + TimescaleDB (prod)
- **Deploy**: Docker, Docker Compose

---


</div>
