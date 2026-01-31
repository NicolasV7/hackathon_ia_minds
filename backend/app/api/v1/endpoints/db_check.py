"""
Database verification endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.dependencies import get_db

router = APIRouter(prefix="/db-check", tags=["database"])

@router.get("/status")
async def check_database_status(db: AsyncSession = Depends(get_db)):
    """Check database connection and record count."""
    try:
        # Check connection
        result = await db.execute(text("SELECT 1"))
        await result.scalar()
        
        # Check table exists
        result = await db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'consumption_records'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            return {
                "status": "error",
                "message": "Table consumption_records does not exist",
                "record_count": 0
            }
        
        # Get record count
        result = await db.execute(text("SELECT COUNT(*) FROM consumption_records"))
        count = result.scalar()
        
        # Get sample by sede
        result = await db.execute(text("""
            SELECT sede, COUNT(*) as count 
            FROM consumption_records 
            GROUP BY sede 
            ORDER BY sede
        """))
        by_sede = [{"sede": row[0], "count": row[1]} for row in result.fetchall()]
        
        return {
            "status": "healthy" if count > 0 else "empty",
            "record_count": count,
            "by_sede": by_sede,
            "message": f"Database has {count} records" if count > 0 else "Database is empty - run data load"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "record_count": 0
        }
