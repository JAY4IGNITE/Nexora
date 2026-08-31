from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.user import User, UserRole
from app.api.deps import require_roles
from app.core.supabase import get_supabase_client
from app.services.ingestion.provider import MockJobProvider
from app.services.ingestion.adzuna import AdzunaProvider
from app.services.ingestion.pipeline import PipelineEngine

router = APIRouter()

@router.post("/ingest", status_code=status.HTTP_200_OK)
def trigger_ingestion(
    provider_name: str = Query("mock", description="Provider to use: 'mock' or 'adzuna'"),
    keyword: str = Query("", description="Keyword search (Adzuna)"),
    location: str = Query("", description="Location search (Adzuna)"),
    page: int = Query(1, description="Page number (Adzuna)"),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    """
    Triggers the labour market ingestion pipeline.
    Restricted to ADMIN users.
    """
    try:
        db = get_supabase_client()
        
        if provider_name.lower() == "adzuna":
            provider = AdzunaProvider(keyword=keyword, location=location, page=page)
        else:
            provider = MockJobProvider()
            
        engine = PipelineEngine(db=db, provider=provider)
        
        metrics = engine.run()
        return {
            "status": "success",
            "message": f"Ingestion pipeline completed using {provider.get_provider_name()}.",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion pipeline failed: {str(e)}"
        )

@router.get("/ingestion-runs")
def list_ingestion_runs(limit: int = 10, current_user: User = Depends(require_roles([UserRole.ADMIN]))):
    """List recent ingestion runs (Admin only)."""
    db = get_supabase_client()
    try:
        res = db.table('job_ingestion_runs').select('*').order('created_at', desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
def get_labour_market_statistics():
    """Publicly accessible high-level stats of the database."""
    db = get_supabase_client()
    try:
        # Simple counts using Supabase client
        jobs_count = db.table('job_postings').select('id', count='exact').execute()
        sectors = db.table('sectors').select('id, name').execute()
        
        # We can't do complex group_bys natively via postgrest easily without RPC, 
        # so we'll fetch jobs and group in python for this MVP demonstration.
        # In a real heavy app, we'd use a postgres VIEW or RPC.
        jobs = db.table('job_postings').select('sector_id, district_id, job_role_id').execute()
        
        sector_counts = {}
        for j in jobs.data:
            sid = j.get('sector_id')
            if sid:
                sector_counts[sid] = sector_counts.get(sid, 0) + 1
                
        # Resolve names
        sector_stats = []
        for s in sectors.data:
            sector_stats.append({
                "sector": s['name'],
                "count": sector_counts.get(s['id'], 0)
            })
            
        return {
            "total_jobs": jobs_count.count,
            "jobs_by_sector": sector_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
