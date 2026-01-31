-- Script SQL para cargar datos del CSV a PostgreSQL usando COPY
-- Este script debe ejecutarse manualmente una vez en el servidor

-- Verificar que la tabla existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' 
                   AND table_name = 'consumption_records') THEN
        RAISE EXCEPTION 'La tabla consumption_records no existe. Ejecuta primero el init_db.sql';
    END IF;
END $$;

-- Truncar tabla si tiene datos
TRUNCATE TABLE consumption_records RESTART IDENTITY CASCADE;

-- Crear tabla temporal para cargar el CSV
CREATE TEMP TABLE temp_consumption (
    reading_id INTEGER,
    timestamp TIMESTAMP,
    sede VARCHAR(50),
    sede_id VARCHAR(50),
    energia_total_kwh FLOAT,
    energia_comedor_kwh FLOAT,
    energia_salones_kwh FLOAT,
    energia_laboratorios_kwh FLOAT,
    energia_auditorios_kwh FLOAT,
    energia_oficinas_kwh FLOAT,
    potencia_total_kw FLOAT,
    agua_litros FLOAT,
    temperatura_exterior_c FLOAT,
    ocupacion_pct FLOAT,
    hora INTEGER,
    dia_semana INTEGER,
    dia_nombre VARCHAR(20),
    mes INTEGER,
    trimestre INTEGER,
    año INTEGER,
    periodo_academico VARCHAR(50),
    es_fin_semana BOOLEAN,
    es_festivo BOOLEAN,
    es_semana_parciales BOOLEAN,
    es_semana_finales BOOLEAN,
    co2_kg FLOAT
);

-- Copiar datos desde CSV
-- Nota: Ajusta la ruta según donde esté montado el volumen en Docker
COPY temp_consumption FROM '/docker-entrypoint-initdb.d/consumos_uptc.csv' WITH (FORMAT csv, HEADER true, NULL '');

-- Insertar datos en la tabla principal
INSERT INTO consumption_records (
    timestamp,
    sede,
    hora,
    dia_semana,
    mes,
    ano,
    energia_comedor_kwh,
    energia_salones_kwh,
    energia_laboratorios_kwh,
    energia_auditorios_kwh,
    energia_oficinas_kwh,
    energia_total_kwh,
    potencia_total_kw,
    co2_kg,
    agua_litros,
    temperatura_exterior_c,
    ocupacion_pct,
    es_fin_semana,
    es_festivo,
    es_semana_parciales,
    es_semana_finales,
    periodo_academico
)
SELECT 
    timestamp,
    sede,
    hora,
    dia_semana,
    mes,
    año,
    energia_comedor_kwh,
    energia_salones_kwh,
    energia_laboratorios_kwh,
    energia_auditorios_kwh,
    energia_oficinas_kwh,
    energia_total_kwh,
    potencia_total_kw,
    co2_kg,
    agua_litros,
    temperatura_exterior_c,
    ocupacion_pct,
    es_fin_semana,
    es_festivo,
    es_semana_parciales,
    es_semana_finales,
    periodo_academico
FROM temp_consumption;

-- Limpiar tabla temporal
DROP TABLE temp_consumption;

-- Verificar carga
SELECT 
    'Total registros cargados' as mensaje,
    COUNT(*) as total
FROM consumption_records
UNION ALL
SELECT 
    'Registros por sede',
    COUNT(*)
FROM consumption_records
GROUP BY sede;
