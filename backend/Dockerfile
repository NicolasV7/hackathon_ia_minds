# ============================================================================
#  UPTC EcoEnergy Backend - Dockerfile
#  Multi-stage build: builder -> production
# ============================================================================

# ------ Stage 1: Install Python dependencies ------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build-time system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (better Docker layer caching)
COPY backend/requirements.txt .

# Create virtualenv and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ------ Stage 2: Production image ------
FROM python:3.12-slim AS production

# Runtime system dependencies
#   curl    -> healthcheck
#   libgomp1 -> required by LightGBM
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Security: non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appgroup backend/app       ./app
COPY --chown=appuser:appgroup backend/ml_models  ./ml_models
COPY --chown=appuser:appgroup backend/scripts    ./scripts
COPY --chown=appuser:appgroup models             ./models

# Create data directory for SQLite
RUN mkdir -p /app/data && chown appuser:appgroup /app/data

# Python optimizations
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

EXPOSE 8000

# Healthcheck (generous start period for ML model loading + DB init)
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Init DB in background, then start the API server
CMD ["sh", "-c", "(python scripts/init_sqlite.py &) && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
