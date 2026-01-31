#!/usr/bin/env python3
"""
Script para cargar datos del CSV a SQLite.
Se ejecuta automáticamente al iniciar el backend si la base de datos está vacía.
"""

import asyncio
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine, AsyncSessionLocal
from app.models.consumption import ConsumptionRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path al CSV
CSV_PATH = Path(__file__).parent.parent.parent / "consumos_uptc_hackday" / "consumos_uptc.csv"
BATCH_SIZE = 10000


async def load_data_from_csv():
    """Carga datos desde CSV a SQLite."""
    
    if not CSV_PATH.exists():
        logger.error(f"Archivo CSV no encontrado: {CSV_PATH}")
        return False
    
    logger.info(f"Cargando datos desde: {CSV_PATH}")
    
    # Leer CSV con pandas
    df = pd.read_csv(CSV_PATH)
    logger.info(f"Registros en CSV: {len(df)}")
    
    # Limpiar y preparar datos
    df = df.rename(columns={
        'año': 'ano',
        'reading_id': 'id'
    })
    
    # Mapear columnas
    column_mapping = {
        'timestamp': 'timestamp',
        'sede': 'sede',
        'hora': 'hora',
        'dia_semana': 'dia_semana',
        'mes': 'mes',
        'ano': 'ano',
        'energia_comedor_kwh': 'energia_comedor_kwh',
        'energia_salones_kwh': 'energia_salones_kwh',
        'energia_laboratorios_kwh': 'energia_laboratorios_kwh',
        'energia_auditorios_kwh': 'energia_auditorios_kwh',
        'energia_oficinas_kwh': 'energia_oficinas_kwh',
        'energia_total_kwh': 'energia_total_kwh',
        'potencia_total_kw': 'potencia_total_kw',
        'co2_kg': 'co2_kg',
        'agua_litros': 'agua_litros',
        'temperatura_exterior_c': 'temperatura_exterior_c',
        'ocupacion_pct': 'ocupacion_pct',
        'es_fin_semana': 'es_fin_semana',
        'es_festivo': 'es_festivo',
        'es_semana_parciales': 'es_semana_parciales',
        'es_semana_finales': 'es_semana_finales',
        'periodo_academico': 'periodo_academico'
    }
    
    # Seleccionar solo columnas necesarias
    df = df[list(column_mapping.keys())]
    
    # Convertir booleanos
    bool_columns = ['es_fin_semana', 'es_festivo', 'es_semana_parciales', 'es_semana_finales']
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].map({'True': True, 'False': False, True: True, False: False})
    
    # Convertir a diccionarios
    records = df.to_dict('records')
    
    # Insertar en batches
    async with AsyncSessionLocal() as session:
        # Verificar si ya hay datos
        result = await session.execute("SELECT COUNT(*) FROM consumption_records")
        count = result.scalar()
        
        if count > 0:
            logger.info(f"La base de datos ya tiene {count} registros. Omitiendo carga.")
            return True
        
        logger.info(f"Insertando {len(records)} registros...")
        
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i + BATCH_SIZE]
            
            for record_data in batch:
                record = ConsumptionRecord(**record_data)
                session.add(record)
            
            await session.commit()
            logger.info(f"Batch {i//BATCH_SIZE + 1}/{(len(records) + BATCH_SIZE - 1)//BATCH_SIZE} completado")
    
    logger.info("✅ Carga de datos completada!")
    return True


if __name__ == "__main__":
    asyncio.run(load_data_from_csv())
