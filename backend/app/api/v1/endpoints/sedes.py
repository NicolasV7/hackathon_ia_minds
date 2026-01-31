"""
Sedes endpoint - returns list of campuses (sedes) available in dataset.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import csv
import os

router = APIRouter(prefix="/sedes", tags=["sedes"])


@router.get("", response_model=List[Dict])
async def list_sedes():
    csv_path = "/app/data/csv/sedes_uptc.csv"
    if not os.path.exists(csv_path):
        # fallback: try repo file
        csv_path = os.path.join(os.path.dirname(__file__), "../../../../../../consumos_uptc_hackday/sedes_uptc.csv")
        csv_path = os.path.normpath(csv_path)

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Sedes data not found")

    sedes = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize to frontend expected shape
                sedes.append({
                    "id": (row.get("sede") or '').lower(),
                    "sede_id": row.get("sede_id"),
                    "nombre": row.get("nombre_completo") or row.get("sede"),
                    "ciudad": row.get("ciudad"),
                    "estudiantes": int(row.get("num_estudiantes", 0)) if row.get("num_estudiantes") else 0,
                    # placeholders for frontend fields
                    "lat": float(row.get("lat")) if row.get("lat") else 0.0,
                    "lng": float(row.get("lng")) if row.get("lng") else 0.0,
                    "consumo_energia": 0,
                    "consumo_agua": 0,
                    "emisiones_co2": 0,
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return sedes
