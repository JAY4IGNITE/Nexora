from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.core.supabase import get_supabase_client
from app.services.intelligence.gap_explainer import generate_gap_explanation

router = APIRouter()

class GapResult(BaseModel):
    skill_id: str
    skill_name: str
    skill_category: str
    demand_count: int
    demand_priority: str
    coverage_count: int
    coverage_status: str
    alignment_status: str
    explanation: str

@router.get("/overview")
def get_curriculum_overview():
    """
    Returns a high-level overview of curriculum and training coverage.
    """
    db = get_supabase_client()
    try:
        curricula = db.table('curricula').select('id', count='exact').execute()
        courses = db.table('courses').select('id', count='exact').execute()
        mapped_skills = db.table('view_curriculum_alignment').select('skill_id', count='exact').gt('total_coverage_count', 0).execute()
        
        return {
            "total_curricula": curricula.count,
            "total_training_programs": courses.count,
            "skills_covered": mapped_skills.count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alignment")
def get_curriculum_alignment(limit: int = 20):
    """
    Returns the alignment of industry-demanded skills against curriculum and training availability.
    Sorted by gap_priority descending (most critical missing coverage first).
    """
    db = get_supabase_client()
    try:
        res = db.table('view_curriculum_alignment')\
                .select('*')\
                .order('gap_priority', desc=True)\
                .limit(limit)\
                .execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gaps", response_model=List[GapResult])
async def get_curriculum_gaps(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    alignment: Optional[str] = None
):
    """Returns the core curriculum gap intelligence."""
    db = get_supabase_client()
    
    query = db.table('view_curriculum_gap_intelligence').select('*')
    if alignment:
        query = query.eq('alignment_status', alignment)
    else:
        # Default to showing actual gaps
        query = query.in_('alignment_status', ['UNDER_COVERED', 'NOT_COVERED', 'PARTIALLY_ALIGNED'])
        
    res = query.order('demand_count', desc=True).range(offset, offset + limit - 1).execute()
    
    results = []
    for r in res.data:
        expl = generate_gap_explanation(
            r['skill_name'], r['alignment_status'], r['demand_priority'], 
            r['demand_count'], r['coverage_status'], r['coverage_count']
        )
        r['explanation'] = expl
        results.append(GapResult(**r))
        
    return results

@router.get("/role-alignment/{role_id}")
async def get_role_alignment(
    role_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Returns curriculum gaps specific to a job role."""
    db = get_supabase_client()
    
    res = db.table('view_role_curriculum_alignment').select('*').eq('job_role_id', role_id).order('role_demand_count', desc=True).range(offset, offset + limit - 1).execute()
    
    results = []
    for r in res.data:
        expl = generate_gap_explanation(
            r['skill_name'], r['alignment_status'], r['demand_priority'], 
            r['role_demand_count'], r['coverage_status'], r['coverage_count'],
            is_role_context=True, role_name=r['job_role_name']
        )
        r['explanation'] = expl
        results.append(r)
        
    return results
