import os
import sys
from dotenv import load_dotenv

# Ensure env vars are loaded before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from app.core.supabase import get_supabase_client

def seed_controlled_test_data():
    print("--- SEEDING MODULE 6 CONTROLLED TEST DATA ---")
    db = get_supabase_client()
    
    print("1. Creating Skills: Python, SQL, MLOps, LLMOps")
    skills = [
        {"name": "Python", "normalized_name": "python", "category": "Programming", "description": "Python Programming"},
        {"name": "SQL", "normalized_name": "sql", "category": "Database", "description": "Structured Query Language"},
        {"name": "MLOps", "normalized_name": "mlops", "category": "AI/ML", "description": "Machine Learning Operations"},
        {"name": "LLMOps", "normalized_name": "llmops", "category": "AI/ML", "description": "Large Language Model Operations"}
    ]
    inserted_skills = []
    for s in skills:
        res = db.table('skills').upsert(s, on_conflict='normalized_name').execute()
        # Fetch the ID because upsert might not return it if it already exists
        skill_res = db.table('skills').select('id, name').eq('normalized_name', s['normalized_name']).execute()
        inserted_skills.append(skill_res.data[0])
    
    skill_map = {s['name']: s['id'] for s in inserted_skills}
    print("   Skills verified.")

    print("2. Generating Industry Demand (Dummy Job Postings)")
    # To hit the threshold (Coverage < Demand / 2 = UNDER_COVERED)
    # Python: Demand 4, Curr 1, Train 1 => Total 2. (2 < 4/2 is false) -> ALIGNED
    # SQL: Demand 4, Curr 1, Train 1 => Total 2 -> ALIGNED
    # MLOps: Demand 4, Curr 0, Train 1 => Total 1. (1 < 4/2 is true) -> UNDER_COVERED
    # LLMOps: Demand 4, Curr 0, Train 0 => Total 0 -> NOT_COVERED

    # First, create a dummy job role
    role_res = db.table('job_roles').upsert({"name": "Test Data Scientist", "description": "Test"}).execute()
    role_id = db.table('job_roles').select('id').eq('name', "Test Data Scientist").execute().data[0]['id']

    # Create 4 dummy job postings
    job_ids = []
    for i in range(4):
        post = db.table('job_postings').insert({
            "title": f"Test Data Scientist {i}",
            "source": "manual_test",
            "job_role_id": role_id
        }).execute()
        job_ids.append(post.data[0]['id'])
    
    # Map all 4 jobs to all 4 skills so each skill has exactly Demand=4
    for jid in job_ids:
        for sid in skill_map.values():
            db.table('job_posting_skills').upsert({"job_posting_id": jid, "skill_id": sid}).execute()
            
    print("   Industry demand seeded (Demand=4 for all).")

    print("3. Seeding Curriculum Coverage (Python, SQL)")
    # Create an institution
    inst_res = db.table('users').insert({
        "email": "test_inst@nexora.com", 
        "firebase_uid": "test_inst_firebase", 
        "role": "INSTITUTION"
    }).execute()
    inst_id = inst_res.data[0]['id']

    curr = db.table('curricula').insert({
        "institution_id": inst_id,
        "program_name": "Test CS Degree"
    }).execute()
    curr_id = curr.data[0]['id']
    
    db.table('curriculum_skills').upsert({"curriculum_id": curr_id, "skill_id": skill_map['Python'], "coverage_level": "COVERED"}).execute()
    db.table('curriculum_skills').upsert({"curriculum_id": curr_id, "skill_id": skill_map['SQL'], "coverage_level": "COVERED"}).execute()
    print("   Curriculum coverage seeded.")

    print("4. Seeding Training Coverage (Python, SQL, MLOps)")
    # Create a training provider course
    course = db.table('courses').insert({
        "name": "Test Data Bootcamp",
        "provider_id": inst_id
    }).execute()
    course_id = course.data[0]['id']
    
    db.table('course_skills').upsert({"course_id": course_id, "skill_id": skill_map['Python'], "coverage_level": "COVERED"}).execute()
    db.table('course_skills').upsert({"course_id": course_id, "skill_id": skill_map['SQL'], "coverage_level": "COVERED"}).execute()
    db.table('course_skills').upsert({"course_id": course_id, "skill_id": skill_map['MLOps'], "coverage_level": "INTRODUCTORY"}).execute()
    # LLMOps remains unmapped everywhere.
    print("   Training coverage seeded.")
    
    print("--- SEEDING COMPLETE ---")

if __name__ == "__main__":
    seed_controlled_test_data()
