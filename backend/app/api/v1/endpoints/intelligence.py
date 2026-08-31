from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User, UserRole
from app.api.deps import require_roles
from app.core.supabase import get_supabase_client

router = APIRouter()

@router.get("/demand/skills")
def get_demand_by_skills(limit: int = 10):
    db = get_supabase_client()
    try:
        # We order by demand_count descending
        res = db.table('view_demand_by_skill').select('*').order('demand_count', desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demand/roles")
def get_demand_by_roles(limit: int = 10):
    db = get_supabase_client()
    try:
        res = db.table('view_demand_by_role').select('*').order('demand_count', desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demand/sectors")
def get_demand_by_sectors(limit: int = 10):
    db = get_supabase_client()
    try:
        res = db.table('view_demand_by_sector').select('*').order('demand_count', desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demand/geography")
def get_demand_by_geography(limit: int = 10):
    db = get_supabase_client()
    try:
        res = db.table('view_demand_by_district').select('*').order('demand_count', desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/skills")
def get_skill_trends(limit_skills: int = 5):
    """
    Returns time-series data for the top N skills.
    To make charting easy on the frontend, we'll format it.
    """
    db = get_supabase_client()
    try:
        # First, find the top skills overall to filter the trends
        top_skills = db.table('view_demand_by_skill').select('skill_id').order('demand_count', desc=True).limit(limit_skills).execute()
        if not top_skills.data:
            return []
            
        top_ids = [s['skill_id'] for s in top_skills.data]
        
        # Then get their trends
        res = db.table('view_skill_trends').select('*').in_('skill_id', top_ids).order('month').execute()
        
        # Reformat for frontend Recharts: 
        # [{ month: '2026-08', 'Python': 15, 'React': 10 }, ...]
        
        # 1. Group by month
        data_by_month = {}
        for row in res.data:
            month = row['month'].split('T')[0][:7] # YYYY-MM
            skill_name = row['skill_name']
            count = row['demand_count']
            
            if month not in data_by_month:
                data_by_month[month] = {'month': month}
            data_by_month[month][skill_name] = count
            
        # 2. Convert to list and sort chronologically
        chart_data = list(data_by_month.values())
        chart_data.sort(key=lambda x: x['month'])
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/roles")
def get_role_trends(limit_roles: int = 5):
    db = get_supabase_client()
    try:
        top_roles = db.table('view_demand_by_role').select('role_id').order('demand_count', desc=True).limit(limit_roles).execute()
        if not top_roles.data:
            return []
            
        top_ids = [r['role_id'] for r in top_roles.data]
        res = db.table('view_role_trends').select('*').in_('role_id', top_ids).order('month').execute()
        
        data_by_month = {}
        for row in res.data:
            month = row['month'].split('T')[0][:7]
            role_name = row['role_name']
            count = row['demand_count']
            
            if month not in data_by_month:
                data_by_month[month] = {'month': month}
            data_by_month[month][role_name] = count
            
        chart_data = list(data_by_month.values())
        chart_data.sort(key=lambda x: x['month'])
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/gap/skills')
def get_demand_supply_gap(limit: int = 20):
    db = get_supabase_client()
    try:
        res = db.table('view_demand_supply_gap').select('*').order('net_gap', desc=False).limit(limit).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
