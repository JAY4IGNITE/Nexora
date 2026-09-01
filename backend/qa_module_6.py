import os
from dotenv import load_dotenv

# Ensure env vars are loaded before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.core.supabase import get_supabase_client

def run_qa():
    print("\n--- NEXORA MODULE 6 QA VERIFICATION ---\n")
    
    db = get_supabase_client()
    
    print("1. Fetching Curriculum Alignment (from API endpoint equivalent)...")
    try:
        from app.api.v1.endpoints.curriculum import get_curriculum_alignment
        
        # Testing API
        alignment = get_curriculum_alignment(limit=10)
        print(f"[PASS] Retrieved {len(alignment)} alignment records.")
        
        print("\n2. Validating Classifications:")
        for row in alignment:
            print(f" -> {row['skill_name']:<15} | Demand: {row['industry_demand_count']:<3} | Curr: {row['curriculum_program_count']:<3} | Train: {row['training_program_count']:<3} | Class: {row['classification']}")
            
            # Mathematical validation
            d = row['industry_demand_count']
            cov = row['total_coverage_count']
            
            if d == 0:
                assert row['classification'] == 'NO_DEMAND'
            elif cov == 0:
                assert row['classification'] == 'NOT_COVERED'
            elif cov < d / 2:
                assert row['classification'] == 'UNDER_COVERED'
            else:
                assert row['classification'] == 'ALIGNED'
                
        print("\n[PASS] All alignment mathematics are correct and purely evidence-based.")
        
    except Exception as e:
        print(f"[FAIL] QA Error: {e}")

    print("\n--- QA COMPLETE ---")

if __name__ == "__main__":
    run_qa()
