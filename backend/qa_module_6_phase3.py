import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure backend is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from app.core.supabase import get_supabase_client
from app.services.intelligence.gap_explainer import generate_gap_explanation

def test_gap_engine():
    print("--- TESTING GAP ENGINE ---")
    db = get_supabase_client()
    
    # 1. Fetch Global Alignment
    print("\n1. Fetching Global Gaps...")
    res = db.table('view_curriculum_gap_intelligence').select('*').limit(5).execute()
    
    if res.data:
        for r in res.data:
            print(f"Skill: {r['skill_name']}")
            print(f"  Demand: {r['demand_priority']} ({r['demand_count']})")
            print(f"  Coverage: {r['coverage_status']} ({r['coverage_count']})")
            print(f"  Alignment: {r['alignment_status']}")
            
            expl = generate_gap_explanation(
                r['skill_name'], r['alignment_status'], r['demand_priority'], 
                r['demand_count'], r['coverage_status'], r['coverage_count']
            )
            print(f"  Explanation: {expl}")
            print("-" * 40)
    else:
        print("No gaps found.")

    # 2. Fetch Role Alignment
    print("\n2. Fetching Role Alignments...")
    res = db.table('view_role_curriculum_alignment').select('*').limit(3).execute()
    if res.data:
        for r in res.data:
            print(f"Role: {r['job_role_name']} | Skill: {r['skill_name']}")
            print(f"  Role Demand: {r['demand_priority']} ({r['role_demand_count']})")
            print(f"  Coverage: {r['coverage_status']} ({r['coverage_count']})")
            print(f"  Alignment: {r['alignment_status']}")
            
            expl = generate_gap_explanation(
                r['skill_name'], r['alignment_status'], r['demand_priority'], 
                r['role_demand_count'], r['coverage_status'], r['coverage_count'],
                is_role_context=True, role_name=r['job_role_name']
            )
            print(f"  Explanation: {expl}")
            print("-" * 40)
    else:
        print("No role alignments found.")
        
    print("\n--- TESTS COMPLETE ---")

if __name__ == "__main__":
    test_gap_engine()
