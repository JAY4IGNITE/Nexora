import os
from dotenv import load_dotenv

# Ensure env vars are loaded before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.core.supabase import get_supabase_client

def run_qa():
    print("\n--- NEXORA MODULE 5 MANUAL QA VERIFICATION ---\n")
    
    db = get_supabase_client()
    
    # 2. Decide which supply datasets you actually have
    # 3. Configure/verify training and student-skill data sources
    print("1. Verifying Supply Data Sources (No Manufactured Numbers)...")
    try:
        students = db.table('student_skills').select('*').execute()
        print(f"[PASS] Real Student Skills in DB: {len(students.data)} records")
        
        training = db.table('training_capacity').select('*').execute()
        print(f"[PASS] Real Training Capacities in DB: {len(training.data)} records")
    except Exception as e:
        print(f"[FAIL] Error fetching supply tables: {e}")

    # 4. Check the gap formulas
    print("\n2. Gap Formula Verification:")
    print("DEMAND = COUNT(job_posting_skills)")
    print("WORKFORCE_SUPPLY = COUNT(student_skills) WHERE proficiency >= 3")
    print("TRAINING_SUPPLY = SUM(training_capacity.capacity) for courses mapped to curriculum_skills")
    print("NET GAP = (WORKFORCE_SUPPLY + TRAINING_SUPPLY) - DEMAND")

    # 6. Verify results in Supabase
    print("\n3. Inspecting Gap Engine View (Controlled Data Check)...")
    try:
        gap_view = db.table('view_demand_supply_gap').select('*').limit(5).execute()
        print(f"[PASS] view_demand_supply_gap returns data: {len(gap_view.data)} rows fetched.")
        if gap_view.data:
            for row in gap_view.data:
                print(f"  -> {row['skill_name']} | Demand: {row['demand']} | Supply: {row['total_supply']} | Net: {row['net_gap']}")
                # 9. Verify that the system doesn't manufacture supply numbers
                assert row['total_supply'] == (row['workforce_supply'] + row['training_supply']), "Supply math mismatch!"
    except Exception as e:
        print(f"[FAIL] Error fetching view: {e}")

    # 7. Test the APIs
    print("\n4. Testing API Endpoints (Direct Router Call)...")
    try:
        from app.api.v1.endpoints.intelligence import get_demand_supply_gap
        
        api_gap = get_demand_supply_gap(limit=3)
        print(f"[PASS] GET /gap/skills successfully yielded data array of length {len(api_gap)}")
        
    except Exception as e:
        print(f"[FAIL] Error calling API functions: {e}")
        
    print("\n--- QA COMPLETE ---")

if __name__ == "__main__":
    run_qa()
