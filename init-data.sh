#!/bin/bash
# Initialization script for PostgreSQL
# This runs automatically when the database container starts

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-'EOSQL'
    -- Create TimescaleDB extension
    CREATE EXTENSION IF NOT EXISTS timescaledb;
    
    -- Verify extension
    SELECT * FROM pg_extension WHERE extname = 'timescaledb';
EOSQL

echo "TimescaleDB extension initialized successfully"
