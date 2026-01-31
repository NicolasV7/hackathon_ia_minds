#!/usr/bin/env python3
"""
Script ETL para cargar datos históricos del CSV a PostgreSQL.

Uso:
    python backend/scripts/load_consumption_data.py

O desde Docker:
    docker exec -it uptc_backend python scripts/load_consumption_data.py
"""

import os
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import asyncio
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CSV_PATH = Path(__file__).parent.parent.parent / "consumos_uptc_hackday" / "consumos_uptc.csv"
SEDES_CSV_PATH = Path(__file__).parent.parent.parent / "consumos_uptc_hackday" / "sedes_uptc.csv"
BATCH_SIZE = 5000

# Database URL from environment or default
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://uptc_user:uptc_password_2024@localhost:5432/uptc_energy"
)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y prepara el DataFrame para inserción.
    
    - Maneja valores nulos
    - Corrige outliers extremos
    - Normaliza tipos de datos
    """
    logger.info("Limpiando datos...")
    
    # Convertir timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Columnas numéricas que pueden tener NaN
    numeric_cols = [
        'energia_total_kwh', 'energia_comedor_kwh', 'energia_salones_kwh',
        'energia_laboratorios_kwh', 'energia_auditorios_kwh', 'energia_oficinas_kwh',
        'potencia_total_kw', 'agua_litros', 'temperatura_exterior_c',
        'ocupacion_pct', 'co2_kg'
    ]
    
    # Reemplazar strings vacíos con NaN
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Manejar outliers extremos en energia_total_kwh
    # Valores negativos o mayores a 50 kWh por hora son probablemente errores
    energy_cols = [c for c in numeric_cols if 'energia' in c or 'kwh' in c.lower()]
    for col in energy_cols:
        if col in df.columns:
            # Reemplazar valores negativos con NaN
            df.loc[df[col] < 0, col] = np.nan
            # Cap outliers extremos (>10 veces la mediana)
            median = df[col].median()
            if pd.notna(median) and median > 0:
                threshold = median * 10
                df.loc[df[col] > threshold, col] = threshold
    
    # Asegurar que energia_total_kwh no sea nulo (columna requerida)
    # Si es nulo, calcular como suma de sectores
    mask = df['energia_total_kwh'].isna()
    sector_cols = ['energia_comedor_kwh', 'energia_salones_kwh', 
                   'energia_laboratorios_kwh', 'energia_auditorios_kwh', 
                   'energia_oficinas_kwh']
    df.loc[mask, 'energia_total_kwh'] = df.loc[mask, sector_cols].sum(axis=1)
    
    # Si todavía hay nulos, usar la mediana por sede y hora
    if df['energia_total_kwh'].isna().any():
        df['energia_total_kwh'] = df.groupby(['sede', 'hora'])['energia_total_kwh'].transform(
            lambda x: x.fillna(x.median())
        )
    
    # Último recurso: llenar con mediana global
    df['energia_total_kwh'] = df['energia_total_kwh'].fillna(df['energia_total_kwh'].median())
    
    # Normalizar booleanos
    bool_cols = ['es_fin_semana', 'es_festivo', 'es_semana_parciales', 'es_semana_finales']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
    
    # Limpiar periodo_academico
    if 'periodo_academico' in df.columns:
        df['periodo_academico'] = df['periodo_academico'].fillna('desconocido')
        # Normalizar valores
        periodo_map = {
            'vacaciones_fin': 'vacaciones',
            'vacaciones_mitad': 'vacaciones',
            'semestre1': 'semestre_1',
            'semestre2': 'semestre_2',
            'semestre_1': 'semestre_1',
            'semestre_2': 'semestre_2',
        }
        df['periodo_academico'] = df['periodo_academico'].replace(periodo_map)
    
    # Asegurar que columnas enteras sean int
    int_cols = ['hora', 'dia_semana', 'mes', 'trimestre', 'año']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    
    logger.info(f"Datos limpiados. Shape: {df.shape}")
    return df


def prepare_records(df: pd.DataFrame) -> list:
    """
    Prepara registros para inserción en batch.
    """
    records = []
    
    for _, row in df.iterrows():
        record = {
            'timestamp': row['timestamp'],
            'sede': row['sede'],
            'hora': int(row['hora']),
            'dia_semana': int(row['dia_semana']),
            'mes': int(row['mes']),
            'ano': int(row['año']),
            'energia_comedor_kwh': float(row['energia_comedor_kwh']) if pd.notna(row['energia_comedor_kwh']) else None,
            'energia_salones_kwh': float(row['energia_salones_kwh']) if pd.notna(row['energia_salones_kwh']) else None,
            'energia_laboratorios_kwh': float(row['energia_laboratorios_kwh']) if pd.notna(row['energia_laboratorios_kwh']) else None,
            'energia_auditorios_kwh': float(row['energia_auditorios_kwh']) if pd.notna(row['energia_auditorios_kwh']) else None,
            'energia_oficinas_kwh': float(row['energia_oficinas_kwh']) if pd.notna(row['energia_oficinas_kwh']) else None,
            'energia_total_kwh': float(row['energia_total_kwh']),
            'potencia_total_kw': float(row['potencia_total_kw']) if pd.notna(row['potencia_total_kw']) else None,
            'co2_kg': float(row['co2_kg']) if pd.notna(row['co2_kg']) else None,
            'agua_litros': float(row['agua_litros']) if pd.notna(row['agua_litros']) else None,
            'temperatura_exterior_c': float(row['temperatura_exterior_c']) if pd.notna(row['temperatura_exterior_c']) else None,
            'ocupacion_pct': float(row['ocupacion_pct']) if pd.notna(row['ocupacion_pct']) else None,
            'es_fin_semana': bool(row['es_fin_semana']),
            'es_festivo': bool(row['es_festivo']),
            'es_semana_parciales': bool(row['es_semana_parciales']),
            'es_semana_finales': bool(row['es_semana_finales']),
            'periodo_academico': str(row['periodo_academico']) if pd.notna(row['periodo_academico']) else None,
        }
        records.append(record)
    
    return records


async def check_existing_data(session: AsyncSession) -> int:
    """Verifica si ya hay datos en la tabla."""
    result = await session.execute(text("SELECT COUNT(*) FROM consumption_records"))
    count = result.scalar()
    return count


async def truncate_table(session: AsyncSession):
    """Trunca la tabla para reinsertar datos."""
    await session.execute(text("TRUNCATE TABLE consumption_records RESTART IDENTITY CASCADE"))
    await session.commit()
    logger.info("Tabla consumption_records truncada")


async def insert_batch(session: AsyncSession, records: list):
    """Inserta un batch de registros."""
    if not records:
        return
    
    # Build INSERT statement
    insert_sql = text("""
        INSERT INTO consumption_records (
            timestamp, sede, hora, dia_semana, mes, ano,
            energia_comedor_kwh, energia_salones_kwh, energia_laboratorios_kwh,
            energia_auditorios_kwh, energia_oficinas_kwh, energia_total_kwh,
            potencia_total_kw, co2_kg, agua_litros,
            temperatura_exterior_c, ocupacion_pct,
            es_fin_semana, es_festivo, es_semana_parciales, es_semana_finales,
            periodo_academico
        ) VALUES (
            :timestamp, :sede, :hora, :dia_semana, :mes, :ano,
            :energia_comedor_kwh, :energia_salones_kwh, :energia_laboratorios_kwh,
            :energia_auditorios_kwh, :energia_oficinas_kwh, :energia_total_kwh,
            :potencia_total_kw, :co2_kg, :agua_litros,
            :temperatura_exterior_c, :ocupacion_pct,
            :es_fin_semana, :es_festivo, :es_semana_parciales, :es_semana_finales,
            :periodo_academico
        )
    """)
    
    for record in records:
        await session.execute(insert_sql, record)


async def load_data(force_reload: bool = False):
    """
    Carga principal de datos.
    
    Args:
        force_reload: Si True, borra datos existentes y recarga
    """
    logger.info(f"Iniciando carga de datos desde: {CSV_PATH}")
    
    if not CSV_PATH.exists():
        logger.error(f"Archivo CSV no encontrado: {CSV_PATH}")
        sys.exit(1)
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check existing data
            existing_count = await check_existing_data(session)
            
            if existing_count > 0:
                if force_reload:
                    logger.warning(f"Encontrados {existing_count} registros. Truncando tabla...")
                    await truncate_table(session)
                else:
                    logger.info(f"Ya existen {existing_count} registros en la BD.")
                    logger.info("Use --force para recargar los datos")
                    return
            
            # Read CSV
            logger.info("Leyendo archivo CSV...")
            df = pd.read_csv(CSV_PATH)
            logger.info(f"Registros leídos: {len(df)}")
            
            # Clean data
            df = clean_dataframe(df)
            
            # Prepare records
            logger.info("Preparando registros para inserción...")
            records = prepare_records(df)
            
            # Insert in batches
            total_batches = (len(records) + BATCH_SIZE - 1) // BATCH_SIZE
            logger.info(f"Insertando {len(records)} registros en {total_batches} batches...")
            
            for i in range(0, len(records), BATCH_SIZE):
                batch = records[i:i + BATCH_SIZE]
                await insert_batch(session, batch)
                await session.commit()
                
                batch_num = (i // BATCH_SIZE) + 1
                if batch_num % 10 == 0 or batch_num == total_batches:
                    logger.info(f"Batch {batch_num}/{total_batches} completado")
            
            # Verify
            final_count = await check_existing_data(session)
            logger.info(f"Carga completada. Total registros: {final_count}")
            
            # Refresh continuous aggregates
            logger.info("Actualizando aggregates de TimescaleDB...")
            try:
                await session.execute(text(
                    "CALL refresh_continuous_aggregate('consumption_hourly', NULL, NULL)"
                ))
                await session.execute(text(
                    "CALL refresh_continuous_aggregate('consumption_daily', NULL, NULL)"
                ))
                await session.commit()
                logger.info("Aggregates actualizados")
            except Exception as e:
                logger.warning(f"No se pudieron actualizar aggregates: {e}")
            
        except Exception as e:
            logger.error(f"Error durante la carga: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def show_stats():
    """Muestra estadísticas de los datos cargados."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Total records
            result = await session.execute(text("SELECT COUNT(*) FROM consumption_records"))
            total = result.scalar()
            
            # By sede
            result = await session.execute(text("""
                SELECT sede, COUNT(*) as count, 
                       MIN(timestamp) as min_date, 
                       MAX(timestamp) as max_date,
                       AVG(energia_total_kwh) as avg_kwh
                FROM consumption_records 
                GROUP BY sede 
                ORDER BY sede
            """))
            sedes = result.fetchall()
            
            print("\n" + "="*60)
            print("ESTADÍSTICAS DE DATOS CARGADOS")
            print("="*60)
            print(f"\nTotal de registros: {total:,}")
            print("\nPor sede:")
            print("-"*60)
            for sede in sedes:
                print(f"  {sede[0]:15} | {sede[1]:,} registros | "
                      f"{sede[2].strftime('%Y-%m-%d')} a {sede[3].strftime('%Y-%m-%d')} | "
                      f"Avg: {sede[4]:.2f} kWh")
            print("="*60 + "\n")
            
        finally:
            await engine.dispose()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Carga datos de consumo a PostgreSQL')
    parser.add_argument('--force', action='store_true', 
                        help='Forzar recarga (borra datos existentes)')
    parser.add_argument('--stats', action='store_true',
                        help='Mostrar solo estadísticas (sin cargar)')
    
    args = parser.parse_args()
    
    if args.stats:
        asyncio.run(show_stats())
    else:
        asyncio.run(load_data(force_reload=args.force))
        asyncio.run(show_stats())


if __name__ == "__main__":
    main()
