-- UPTC EcoEnergy Database Initialization Script
-- Creates tables and TimescaleDB hypertables for time-series data

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create enum types
CREATE TYPE sede_enum AS ENUM ('Tunja', 'Duitama', 'Sogamoso', 'Chiquinquira');
CREATE TYPE sector_enum AS ENUM ('comedor', 'salones', 'laboratorios', 'auditorios', 'oficinas');
CREATE TYPE anomaly_severity_enum AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE anomaly_status_enum AS ENUM ('unresolved', 'investigating', 'resolved');
CREATE TYPE recommendation_priority_enum AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE recommendation_status_enum AS ENUM ('pending', 'in_progress', 'implemented', 'rejected');

-- ============================================================================
-- CONSUMPTION RECORDS TABLE (Main time-series data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS consumption_records (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    sede VARCHAR(50) NOT NULL,
    
    -- Temporal features
    hora INTEGER NOT NULL CHECK (hora >= 0 AND hora <= 23),
    dia_semana INTEGER NOT NULL CHECK (dia_semana >= 0 AND dia_semana <= 6),
    mes INTEGER NOT NULL CHECK (mes >= 1 AND mes <= 12),
    ano INTEGER NOT NULL,
    
    -- Energy consumption by sector (kWh)
    energia_comedor_kwh FLOAT,
    energia_salones_kwh FLOAT,
    energia_laboratorios_kwh FLOAT,
    energia_auditorios_kwh FLOAT,
    energia_oficinas_kwh FLOAT,
    energia_total_kwh FLOAT NOT NULL,
    
    -- Additional metrics
    potencia_total_kw FLOAT,
    co2_kg FLOAT,
    agua_litros FLOAT,
    
    -- Context data
    temperatura_exterior_c FLOAT,
    ocupacion_pct FLOAT,
    
    -- Boolean flags
    es_fin_semana BOOLEAN DEFAULT FALSE,
    es_festivo BOOLEAN DEFAULT FALSE,
    es_semana_parciales BOOLEAN DEFAULT FALSE,
    es_semana_finales BOOLEAN DEFAULT FALSE,
    
    -- Academic period
    periodo_academico VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('consumption_records', 'timestamp', 
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 week'
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_consumption_sede_time ON consumption_records (sede, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_consumption_hora ON consumption_records (hora);
CREATE INDEX IF NOT EXISTS idx_consumption_periodo ON consumption_records (periodo_academico);

-- ============================================================================
-- PREDICTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    sede VARCHAR(50) NOT NULL,
    prediction_timestamp TIMESTAMPTZ NOT NULL,
    
    -- Prediction results
    predicted_kwh FLOAT NOT NULL,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Input features used
    temperatura_exterior_c FLOAT,
    ocupacion_pct FLOAT,
    es_festivo BOOLEAN DEFAULT FALSE,
    es_semana_parciales BOOLEAN DEFAULT FALSE,
    es_semana_finales BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('predictions', 'prediction_timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 month'
);

CREATE INDEX IF NOT EXISTS idx_predictions_sede_time ON predictions (sede, prediction_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions (created_at DESC);

-- ============================================================================
-- ANOMALIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    sede VARCHAR(50) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    
    -- Anomaly details
    anomaly_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    
    -- Values
    actual_value FLOAT NOT NULL,
    expected_value FLOAT NOT NULL,
    deviation_pct FLOAT NOT NULL,
    
    -- Description and recommendation
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    
    -- Potential savings
    potential_savings_kwh FLOAT DEFAULT 0,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'unresolved',
    
    -- Metadata
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('anomalies', 'timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 month'
);

CREATE INDEX IF NOT EXISTS idx_anomalies_sede_severity ON anomalies (sede, severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_status ON anomalies (status);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies (anomaly_type);
CREATE INDEX IF NOT EXISTS idx_anomalies_detected ON anomalies (detected_at DESC);

-- ============================================================================
-- RECOMMENDATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    sede VARCHAR(50) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    
    -- Associated anomaly (optional)
    anomaly_id INTEGER REFERENCES anomalies(id) ON DELETE SET NULL,
    
    -- Recommendation details
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    
    -- Expected benefits
    expected_savings_kwh FLOAT DEFAULT 0,
    expected_savings_cop FLOAT DEFAULT 0,
    expected_co2_reduction_kg FLOAT DEFAULT 0,
    
    -- Implementation
    implementation_difficulty VARCHAR(20),
    actions TEXT[], -- Array of action items
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending',
    implemented_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendations_sede_priority ON recommendations (sede, priority);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations (status);
CREATE INDEX IF NOT EXISTS idx_recommendations_anomaly ON recommendations (anomaly_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_created ON recommendations (created_at DESC);

-- ============================================================================
-- CONTINUOUS AGGREGATES (TimescaleDB feature for fast queries)
-- ============================================================================

-- Hourly consumption statistics by sede
CREATE MATERIALIZED VIEW IF NOT EXISTS consumption_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS bucket,
    sede,
    AVG(energia_total_kwh) as avg_kwh,
    MAX(energia_total_kwh) as max_kwh,
    MIN(energia_total_kwh) as min_kwh,
    SUM(energia_total_kwh) as total_kwh,
    COUNT(*) as record_count
FROM consumption_records
GROUP BY bucket, sede
WITH NO DATA;

-- Refresh policy (update every hour)
SELECT add_continuous_aggregate_policy('consumption_hourly',
    start_offset => INTERVAL '1 week',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Daily consumption statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS consumption_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', timestamp) AS bucket,
    sede,
    AVG(energia_total_kwh) as avg_kwh,
    MAX(energia_total_kwh) as max_kwh,
    MIN(energia_total_kwh) as min_kwh,
    SUM(energia_total_kwh) as total_kwh,
    COUNT(*) as record_count
FROM consumption_records
GROUP BY bucket, sede
WITH NO DATA;

SELECT add_continuous_aggregate_policy('consumption_daily',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for consumption_records
CREATE TRIGGER update_consumption_records_updated_at 
    BEFORE UPDATE ON consumption_records
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO uptc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO uptc_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO uptc_user;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Show created tables
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Show hypertables
SELECT 
    hypertable_name,
    num_dimensions
FROM timescaledb_information.hypertables;

-- Success message
DO $$ 
BEGIN 
    RAISE NOTICE 'UPTC EcoEnergy database initialized successfully!';
END $$;
