# ============================================================================
#  UPTC EcoEnergy Telegram Bot - Dockerfile
# ============================================================================

FROM python:3.11-slim

# Runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc libssl-dev libffi-dev ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Security: non-root user
RUN groupadd -g 1001 botgroup && \
    useradd -u 1001 -g botgroup -s /bin/bash -m botuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=botuser:botgroup app.py ./

# Python optimizations
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER botuser

CMD ["python", "app.py"]
