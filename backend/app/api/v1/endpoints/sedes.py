"""
Sedes (Campus locations) endpoints.
Provides information about UPTC campus locations.
"""

import logging
from typing import List, Dict
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sedes", tags=["sedes"])

# UPTC Campus data
SEDES_DATA = [
    {
        "id": "tunja",
        "nombre": "Tunja (Principal)",
        "estudiantes": 18000,
        "lat": 5.5353,
        "lng": -73.3678,
        "consumo_energia": 45000,
        "consumo_agua": 9500,
        "emisiones_co2": 68.5,
        "area_m2": 125000,
        "edificios": 28,
        "sectores": ["Laboratorios", "Comedores", "Aulas", "Oficinas", "Auditorios", "Biblioteca"]
    },
    {
        "id": "duitama",
        "nombre": "Duitama",
        "estudiantes": 5500,
        "lat": 5.8267,
        "lng": -73.0333,
        "consumo_energia": 18200,
        "consumo_agua": 3800,
        "emisiones_co2": 27.3,
        "area_m2": 45000,
        "edificios": 12,
        "sectores": ["Laboratorios", "Aulas", "Oficinas", "Biblioteca"]
    },
    {
        "id": "sogamoso",
        "nombre": "Sogamoso",
        "estudiantes": 6000,
        "lat": 5.7147,
        "lng": -72.9314,
        "consumo_energia": 15500,
        "consumo_agua": 3200,
        "emisiones_co2": 23.2,
        "area_m2": 38000,
        "edificios": 10,
        "sectores": ["Laboratorios", "Aulas", "Oficinas", "Talleres"]
    },
    {
        "id": "chiquinquira",
        "nombre": "Chiquinquira",
        "estudiantes": 2000,
        "lat": 5.6167,
        "lng": -73.8167,
        "consumo_energia": 6800,
        "consumo_agua": 1400,
        "emisiones_co2": 10.2,
        "area_m2": 15000,
        "edificios": 5,
        "sectores": ["Aulas", "Oficinas", "Biblioteca"]
    }
]


@router.get("")
async def get_sedes() -> List[Dict]:
    """
    Get information about all UPTC campus locations.
    
    Returns:
        List of campus locations with consumption and location data
    """
    return SEDES_DATA


@router.get("/{sede_id}")
async def get_sede(sede_id: str) -> Dict:
    """
    Get information about a specific UPTC campus.
    
    Args:
        sede_id: Campus identifier (e.g., 'tunja', 'duitama')
        
    Returns:
        Campus information
    """
    sede = next((s for s in SEDES_DATA if s["id"] == sede_id.lower()), None)
    if not sede:
        raise HTTPException(status_code=404, detail=f"Sede '{sede_id}' not found")
    return sede
