import os
import sys
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.core.supabase import get_supabase_client
from app.services.ingestion.provider import MockJobProvider
from app.services.ingestion.pipeline import PipelineEngine

def run_test():
    print("--- NEXORA PIPELINE TEST ---")
    db = get_supabase_client()
    provider = MockJobProvider()
    engine = PipelineEngine(db=db, provider=provider)
    
    print("Running ingestion engine...")
    metrics = engine.run()
    
    print("\n--- RESULTS ---")
    for k, v in metrics.items():
        print(f"{k}: {v}")
        
    print("\n--- VALIDATION ---")
    assert metrics["records_received"] == 6, "Expected 6 records"
    assert metrics["records_rejected"] == 1, "Expected 1 rejected (missing title)"
    assert metrics["records_duplicate"] == 1, "Expected 1 duplicate"
    # remaining 4:
    assert metrics["records_valid"] == 4, "Expected 4 valid records"
    print("All assertions passed!")
    
if __name__ == "__main__":
    run_test()
