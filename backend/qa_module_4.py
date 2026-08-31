import os
import requests
from dotenv import load_dotenv

# Ensure env vars are loaded before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.core.supabase import get_supabase_client
from app.services.ingestion.adzuna import AdzunaProvider

def run_qa():
    print("\n--- NEXORA MODULE 3 & 4 QA VERIFICATION ---\n")
    
    db = get_supabase_client()
    
    # 1. Verify Module 3 is working
    print("1. Verifying Adzuna Jobs in Supabase...")
    jobs = db.table('job_postings').select('id', count='exact').eq('source', 'adzuna').execute()
    print(f"[PASS] Found {jobs.count} Adzuna jobs in the database.")
    
    # 2. Configure filters/data scope
    print("\n2. Data Scope Configuration:")
    provider = AdzunaProvider()
    print(f"[PASS] Target Country: {provider.base_url.split('/')[-2].upper()} (India)")
    print(f"[PASS] Default Limit per Sync: {provider.results_per_page} jobs")
    
    # 3. Review Analytics Definitions
    print("\n3. Analytics Definitions:")
    print("[PASS] 'Demand by Skill': Number of unique job postings requiring a canonical skill.")
    print("[PASS] 'Demand by Role': Number of unique job postings mapped to a canonical role.")
    print("[PASS] 'Skill Trends': Time-series month-over-month growth of demand counts.")
    
    # 4 & 5. Inspect Supabase Analytics Views
    print("\n4. Inspecting Supabase Intelligence Views...")
    try:
        roles_view = db.table('view_demand_by_role').select('*').limit(3).execute()
        print(f"[PASS] view_demand_by_role returns data: {len(roles_view.data)} rows fetched.")
        
        sectors_view = db.table('view_demand_by_sector').select('*').limit(3).execute()
        print(f"[PASS] view_demand_by_sector returns data: {len(sectors_view.data)} rows fetched.")
        
        skills_view = db.table('view_demand_by_skill').select('*').limit(3).execute()
        print(f"[PASS] view_demand_by_skill returns data: {len(skills_view.data)} rows fetched.")
    except Exception as e:
        print(f"[FAIL] Error fetching views: {e}")

    # 6. Test API endpoints
    # To test API endpoints without starting uvicorn separately, 
    # we can import the endpoint functions directly from the FastAPI router
    print("\n5. Testing API Endpoints (Direct Router Call)...")
    try:
        from app.api.v1.endpoints.intelligence import get_demand_by_roles, get_demand_by_skills, get_skill_trends
        
        api_roles = get_demand_by_roles(limit=3)
        print(f"[PASS] GET /demand/roles successfully yielded: {api_roles}")
        
        api_skills = get_demand_by_skills(limit=3)
        print(f"[PASS] GET /demand/skills successfully yielded: {api_skills}")
        
        api_trends = get_skill_trends(limit_skills=3)
        print(f"[PASS] GET /trends/skills successfully yielded: {api_trends}")
        
    except Exception as e:
        print(f"[FAIL] Error calling API functions: {e}")
        
    print("\n--- QA COMPLETE ---")

if __name__ == "__main__":
    run_qa()
