from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import io
import PyPDF2
import logging

import logging

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.services.storage.r2_client import r2_storage
from app.ai.agents.registry import AgentRegistry
from app.ai.agents.skill_agent import SkillAgentInput

logger = logging.getLogger(__name__)
router = APIRouter()

class SkillReportRequest(BaseModel):
    skill_id: str
    proficiency: int
    source: str = "SELF_REPORTED"

class TargetRoleRequest(BaseModel):
    job_role_id: str

@router.get("/skills")
def get_student_skills(current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    student_id = current_user["id"]
    res = supabase.table("view_student_skill_profile").select("*").eq("student_id", student_id).execute()
    return {"skills": res.data}

@router.get("/skills/{skill_id}")
def get_student_skill_detail(skill_id: str, current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    student_id = current_user["id"]
    res = supabase.table("student_skills").select("*").eq("student_id", student_id).eq("skill_id", skill_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Skill not found for student")
    student_skill_id = res.data[0]["id"]
    ev_res = supabase.table("student_skill_evidence").select("*").eq("student_skill_id", student_skill_id).execute()
    return {"skill": res.data[0], "evidence": ev_res.data}

@router.post("/skills")
def add_student_skill(request: SkillReportRequest, current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    student_id = current_user["id"]
    
    existing = supabase.table("student_skills").select("id").eq("student_id", student_id).eq("skill_id", request.skill_id).execute()
    if existing.data:
        ss_id = existing.data[0]["id"]
    else:
        new_ss = supabase.table("student_skills").insert({
            "student_id": student_id,
            "skill_id": request.skill_id,
            "proficiency": request.proficiency,
            "confidence": 0.5,
            "source": request.source
        }).execute()
        ss_id = new_ss.data[0]["id"]
    
    supabase.table("student_skill_evidence").insert({
        "student_skill_id": ss_id,
        "evidence_type": "SELF_REPORTED",
        "evidence_url": None
    }).execute()
    
    return {"status": "success", "student_skill_id": ss_id}

@router.post("/target-role")
def set_target_role(request: TargetRoleRequest, current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    student_id = current_user["id"]
    
    # Deactivate others
    supabase.table("student_target_roles").update({"status": "INACTIVE"}).eq("student_id", student_id).execute()
    
    res = supabase.table("student_target_roles").upsert({
        "student_id": student_id,
        "job_role_id": request.job_role_id,
        "status": "ACTIVE"
    }, on_conflict="student_id,job_role_id").execute()
    
    return {"status": "success", "data": res.data}

@router.get("/skill-gaps")
def get_skill_gaps(current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    student_id = current_user["id"]
    res = supabase.table("view_student_skill_gaps").select("*").eq("student_id", student_id).execute()
    return {"gaps": res.data}

@router.get("/skill-profile")
def get_skill_profile(current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    student_id = current_user["id"]
    profile = supabase.table("student_profiles").select("*").eq("id", student_id).execute()
    roles = supabase.table("student_target_roles").select("*, job_roles(*)").eq("student_id", student_id).eq("status", "ACTIVE").execute()
    stats = supabase.table("view_student_skill_profile").select("*").eq("student_id", student_id).execute()
    
    return {
        "profile": profile.data[0] if profile.data else None,
        "active_role": roles.data[0] if roles.data else None,
        "total_skills": len(stats.data) if stats.data else 0
    }

@router.post("/resume/analyze")
async def analyze_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if not file.filename.lower().endswith('.pdf') or file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")
        
    student_id = current_user["id"]
    
    # 1. Upload to R2
    file_key = await r2_storage.upload_resume(file, student_id)
    
    # 2. Extract Text
    content = await file.read()
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
        
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
        
    # 3. Use AI Agent
    agent = AgentRegistry.get_agent("SkillIntelligenceAgent")
    try:
        ai_response = await agent.run(SkillAgentInput(text=text))
    except Exception as e:
        logger.error(f"Skill extraction failed: {e}")
        return {"status": "error", "message": "AI Processing failed, try again later.", "file_key": file_key}
        
    extracted = ai_response.result.skills
    
    # 4. Save to DB
    supabase = get_supabase_client()
    
    names = [s.name for s in extracted]
    if not names:
        return {"status": "success", "message": "No skills found", "skills_added": 0}
        
    db_skills = supabase.table("skills").select("id, name").in_("name", names).execute()
    name_to_id = {row["name"]: row["id"] for row in db_skills.data}
    
    added = 0
    for sk in extracted:
        skill_id = name_to_id.get(sk.name)
        if not skill_id:
            continue
            
        prof_map = {"BEGINNER": 2, "INTERMEDIATE": 3, "ADVANCED": 4}
        prof = prof_map.get(sk.proficiency, 2)
        
        # Upsert skill
        res = supabase.table("student_skills").upsert({
            "student_id": student_id,
            "skill_id": skill_id,
            "proficiency": prof,
            "confidence": round(sk.confidence, 2),
            "source": "RESUME",
            "verified_status": True
        }, on_conflict="student_id,skill_id").execute()
        
        ss_id = res.data[0]["id"]
        
        # Insert evidence (we use string RESUME instead of enum because enum was RESUME but sometimes it clashes if typed wrong, but we have enum in schema)
        supabase.table("student_skill_evidence").insert({
            "student_skill_id": ss_id,
            "evidence_type": "RESUME",
            "evidence_url": file_key
        }).execute()
        added += 1
        
    return {
        "status": "success",
        "file_key": file_key,
        "skills_added": added,
        "raw_extracted": [s.model_dump() for s in extracted],
        "reasoning": ai_response.reasoning_summary
    }
