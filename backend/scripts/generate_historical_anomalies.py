"""
Script to generate historical anomalies from consumption data.
Processes all historical data with Isolation Forest to create realistic anomaly history.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.ml.inference import ml_service
from app.repositories.consumption_repository import ConsumptionRepository
from app.repositories.anomaly_repository import AnomalyRepository
from app.schemas.anomaly import AnomalyCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_historical_anomalies():
    """Generate historical anomalies by processing all consumption data."""
    logger.info("Starting historical anomaly generation...")
    
    async with AsyncSessionLocal() as db:
        consumption_repo = ConsumptionRepository()
        anomaly_repo = AnomalyRepository()
        
        # Get date range of all consumption data
        all_consumption = await consumption_repo.get_all(db=db, limit=100000)
        
        if not all_consumption:
            logger.warning("No consumption data found")
            return
        
        # Get unique sedes
        sedes = list(set([c.sede for c in all_consumption]))
        logger.info(f"Found {len(sedes)} sedes: {sedes}")
        
        # Process each sede month by month
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)  # Last 12 months
        
        total_anomalies = 0
        
        for sede in sedes:
            logger.info(f"Processing sede: {sede}")
            
            # Process month by month
            current_date = start_date
            while current_date < end_date:
                month_end = min(current_date + timedelta(days=30), end_date)
                
                # Get consumption data for this month
                month_data = await consumption_repo.get_by_sede_and_date_range(
                    db=db,
                    sede=sede,
                    start_date=current_date,
                    end_date=month_end,
                    limit=10000
                )
                
                if len(month_data) < 10:  # Need minimum data for detection
                    current_date = month_end
                    continue
                
                # Convert to DataFrame format expected by ML service
                import pandas as pd
                consumption_df = []
                for record in month_data:
                    consumption_df.append({
                        'timestamp': record.timestamp,
                        'sede': record.sede,
                        'energia_total_kwh': record.energia_total_kwh,
                        'hora': record.hora if hasattr(record, 'hora') else record.timestamp.hour,
                        'dia_semana': record.dia_semana if hasattr(record, 'dia_semana') else record.timestamp.weekday(),
                        'es_fin_semana': record.es_fin_semana if hasattr(record, 'es_fin_semana') else record.timestamp.weekday() >= 5,
                        'energia_comedor_kwh': getattr(record, 'energia_comedor_kwh', 0),
                        'energia_salones_kwh': getattr(record, 'energia_salones_kwh', 0),
                        'energia_laboratorios_kwh': getattr(record, 'energia_laboratorios_kwh', 0),
                        'energia_auditorios_kwh': getattr(record, 'energia_auditorios_kwh', 0),
                        'energia_oficinas_kwh': getattr(record, 'energia_oficinas_kwh', 0)
                    })
                
                df = pd.DataFrame(consumption_df)
                
                # Detect anomalies with lower contamination for historical data
                detected = ml_service.detect_anomalies(
                    consumption_data=df,
                    contamination=0.05,  # 5% anomalies (lower for historical)
                    severity_threshold=None
                )
                
                # Save detected anomalies with historical dates
                for anomaly in detected:
                    try:
                        # Use the actual timestamp from the consumption record
                        anomaly_create = AnomalyCreate(
                            timestamp=anomaly['timestamp'],
                            sede=anomaly['sede'],
                            sector=anomaly['sector'],
                            anomaly_type=anomaly['anomaly_type'],
                            severity=anomaly['severity'],
                            observed_value_kwh=anomaly['actual_value'],
                            expected_value_kwh=anomaly['expected_value'],
                            deviation_kwh=abs(anomaly['actual_value'] - anomaly['expected_value']),
                            deviation_percentage=anomaly['deviation_pct'],
                            anomaly_score=anomaly.get('anomaly_score', 0),
                            description=anomaly['description'],
                            recommendation=anomaly['recommendation'],
                            potential_savings_kwh=anomaly.get('potential_savings_kwh', 0),
                            detection_method='isolation_forest',
                            status='open'
                        )
                        
                        await anomaly_repo.create(db, anomaly_create)
                        total_anomalies += 1
                        
                    except Exception as e:
                        logger.error(f"Error saving anomaly: {e}")
                        continue
                
                logger.info(f"  {current_date.strftime('%Y-%m')}: {len(detected)} anomalies detected")
                
                # Commit every month
                await db.commit()
                
                current_date = month_end
        
        logger.info(f"Historical anomaly generation complete! Total anomalies: {total_anomalies}")


if __name__ == "__main__":
    asyncio.run(generate_historical_anomalies())
