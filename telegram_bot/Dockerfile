FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps required for building Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libssl-dev \
       libffi-dev \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# Upgrade pip, setuptools and wheel first to reduce many build issues
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py ./

CMD ["python", "app.py"]
