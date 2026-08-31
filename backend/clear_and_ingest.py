import os
from dotenv import load_dotenv

# Ensure env vars are loaded before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.core.supabase import get_supabase_client
from app.services.ingestion.adzuna import AdzunaProvider
from app.services.ingestion.pipeline import PipelineEngine

def clear_and_ingest():
    db = get_supabase_client()
    
    print("1. Clearing old mock data...")
    try:
        # Delete from job_postings where source is MockBoard
        res = db.table('job_postings').delete().eq('source', 'MockBoard').execute()
        print(f"Cleared MockBoard jobs: {len(res.data)}")
        
        # Also clean up adzuna jobs if any were partially created during testing
        res_adzuna = db.table('job_postings').delete().eq('source', 'adzuna').execute()
        print(f"Cleared old Adzuna jobs: {len(res_adzuna.data)}")
        
        # Clear ingestion runs
        res_runs = db.table('job_ingestion_runs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"Cleared {len(res_runs.data)} old ingestion runs.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

    print("\n2. Initializing live Adzuna ingestion (Page 1, 50 results)...")
    try:
        # We fetch 50 results for a solid live dataset
        provider = AdzunaProvider(results_per_page=50, page=1)
        engine = PipelineEngine(db=db, provider=provider)
        
        metrics = engine.run()
        print("\n--- INGESTION RESULTS ---")
        for k, v in metrics.items():
            print(f"{k}: {v}")
            
    except Exception as e:
        print(f"Error during ingestion: {e}")

if __name__ == "__main__":
    clear_and_ingest()
