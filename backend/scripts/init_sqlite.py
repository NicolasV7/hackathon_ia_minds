#!/usr/bin/env python3
"""
Script de inicialización de SQLite - Crea tablas y carga datos desde CSV
"""

import asyncio
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import engine, AsyncSessionLocal, Base
from app.models.consumption import ConsumptionRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path al CSV
CSV_PATH = Path("/app/data/csv/consumos_uptc.csv")
BATCH_SIZE = 5000


async def migrate_predictions_table():
    """Migra la tabla predictions para agregar nuevas columnas si no existen."""
    new_columns = [
        ("predicted_co2_kg", "FLOAT"),
        ("confidence_co2", "FLOAT DEFAULT 0.893"),
        ("predicted_energy_kwh", "FLOAT"),
        ("confidence_energy", "FLOAT DEFAULT 0.998"),
        ("energia_comedor_kwh", "FLOAT"),
        ("energia_salones_kwh", "FLOAT"),
        ("energia_laboratorios_kwh", "FLOAT"),
        ("energia_auditorios_kwh", "FLOAT"),
        ("energia_oficinas_kwh", "FLOAT"),
        ("agua_litros", "FLOAT"),
        ("temperatura_exterior_c", "FLOAT"),
        ("ocupacion_pct", "FLOAT"),
        ("es_festivo", "BOOLEAN DEFAULT 0"),
        ("es_semana_parciales", "BOOLEAN DEFAULT 0"),
        ("es_semana_finales", "BOOLEAN DEFAULT 0"),
        ("model_type_co2", "VARCHAR(50) DEFAULT 'LightGBM'"),
        ("model_type_energy", "VARCHAR(50) DEFAULT 'Ridge'"),
        ("actual_co2_kg", "FLOAT"),
        ("actual_energy_kwh", "FLOAT"),
        ("co2_prediction_error", "FLOAT"),
        ("co2_absolute_error", "FLOAT"),
        ("co2_percentage_error", "FLOAT"),
        ("energy_prediction_error", "FLOAT"),
        ("energy_absolute_error", "FLOAT"),
        ("energy_percentage_error", "FLOAT"),
    ]
    
    async with AsyncSessionLocal() as session:
        # First, drop and recreate predictions table to avoid constraint issues
        # SQLite doesn't support ALTER TABLE to modify constraints easily
        try:
            # Check if old table has data
            result = await session.execute(text("SELECT COUNT(*) FROM predictions"))
            old_count = result.scalar()
            
            if old_count == 0:
                # No data, safe to drop and recreate
                logger.info("Tabla predictions vacía, recreando con nuevo esquema...")
                await session.execute(text("DROP TABLE IF EXISTS predictions"))
                await session.commit()
                logger.info("✅ Tabla predictions eliminada para recreación")
                return  # Will be created by create_all
            else:
                logger.info(f"Tabla predictions tiene {old_count} registros, agregando columnas...")
        except Exception as e:
            logger.info(f"Tabla predictions no existe o error: {e}")
            return  # Will be created by create_all
        
    async with AsyncSessionLocal() as session:
        # Check if predictions table exists
        result = await session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'"
        ))
        if not result.scalar():
            logger.info("Tabla predictions no existe, se creará con create_all")
            return
        
        # Get existing columns
        result = await session.execute(text("PRAGMA table_info(predictions)"))
        existing_columns = {row[1] for row in result.fetchall()}
        
        # Add missing columns
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                try:
                    await session.execute(text(
                        f"ALTER TABLE predictions ADD COLUMN {col_name} {col_type}"
                    ))
                    await session.commit()
                    logger.info(f"✅ Columna agregada: {col_name}")
                except Exception as e:
                    logger.warning(f"No se pudo agregar columna {col_name}: {e}")


async def init_database():
    """Inicializa la base de datos SQLite."""
    logger.info("🚀 Inicializando base de datos SQLite...")
    
    # Crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Tablas creadas")
    
    # Migrar tabla predictions si es necesario
    await migrate_predictions_table()
    logger.info("✅ Migraciones aplicadas")
    
    # Verificar si ya hay datos
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM consumption_records"))
        count = result.scalar()
        
        if count > 0:
            logger.info(f"✅ Base de datos ya tiene {count} registros. Omitiendo carga.")
            return
    
    # Cargar datos desde CSV
    if not CSV_PATH.exists():
        logger.error(f"❌ Archivo CSV no encontrado: {CSV_PATH}")
        return
    
    logger.info(f"📊 Cargando datos desde: {CSV_PATH}")
    
    # Leer CSV
    df = pd.read_csv(CSV_PATH)
    total_records = len(df)
    logger.info(f"📋 Total de registros en CSV: {total_records}")
    
    # Preparar datos
    df = df.rename(columns={'año': 'ano'})
    
    # Convertir timestamp a datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Mapear columnas necesarias
    columns_needed = [
        'timestamp', 'sede', 'hora', 'dia_semana', 'mes', 'ano',
        'energia_comedor_kwh', 'energia_salones_kwh', 'energia_laboratorios_kwh',
        'energia_auditorios_kwh', 'energia_oficinas_kwh', 'energia_total_kwh',
        'potencia_total_kw', 'co2_kg', 'agua_litros',
        'temperatura_exterior_c', 'ocupacion_pct',
        'es_fin_semana', 'es_festivo', 'es_semana_parciales', 'es_semana_finales',
        'periodo_academico'
    ]
    
    df = df[columns_needed]
    
    # Convertir booleanos
    bool_columns = ['es_fin_semana', 'es_festivo', 'es_semana_parciales', 'es_semana_finales']
    for col in bool_columns:
        df[col] = df[col].map({'True': True, 'False': False, True: True, False: False})
    
    # Convertir a diccionarios
    records = df.to_dict('records')
    
    # Insertar en batches
    logger.info(f"💾 Insertando {total_records} registros en batches de {BATCH_SIZE}...")
    
    async with AsyncSessionLocal() as session:
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i + BATCH_SIZE]
            
            for record_data in batch:
                record = ConsumptionRecord(**record_data)
                session.add(record)
            
            await session.commit()
            
            progress = min(i + BATCH_SIZE, total_records)
            percent = (progress / total_records) * 100
            logger.info(f"⏳ Progreso: {progress}/{total_records} ({percent:.1f}%)")
    
    logger.info("✅ Carga de datos completada!")
    
    # Verificar carga
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT sede, COUNT(*) as count 
            FROM consumption_records 
            GROUP BY sede 
            ORDER BY sede
        """))
        by_sede = result.fetchall()
        
        logger.info("📊 Resumen por sede:")
        for sede, count in by_sede:
            logger.info(f"   {sede}: {count} registros")


if __name__ == "__main__":
    asyncio.run(init_database())
