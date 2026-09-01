from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.core.supabase import get_supabase_client

router = APIRouter()

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
