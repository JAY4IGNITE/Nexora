import os
import sys
from unittest import mock
from dotenv import load_dotenv

# Ensure env vars are loaded before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.services.ingestion.adzuna import AdzunaProvider
from app.core.supabase import get_supabase_client
from app.services.ingestion.pipeline import PipelineEngine

MOCK_ADZUNA_RESPONSE = {
    "results": [
        {
            "id": "1234567890",
            "redirect_url": "https://www.adzuna.com/job/1234567890",
            "title": "Software Engineer (Python/Django)",
            "company": {"display_name": "Tech Corp India"},
            "description": "Looking for a python developer with React experience.",
            "location": {"area": ["India", "Maharashtra", "Mumbai"]},
            "contract_type": "full_time",
            "contract_time": "permanent",
            "salary_min": 500000,
            "salary_max": 1000000,
            "created": "2026-08-31T10:00:00Z"
        },
        {
            "id": "0987654321",
            "redirect_url": "https://www.adzuna.com/job/0987654321",
            "title": "", # Invalid (missing title)
            "company": {"display_name": "NoTitle Co"},
            "description": "No title here.",
            "location": {"area": ["India", "Delhi"]},
            "created": "2026-08-31T10:00:00Z"
        }
    ]
}

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP Error")


@mock.patch('app.services.ingestion.adzuna.requests.get')
def run_test(mock_get):
    print("--- NEXORA ADZUNA MOCK TEST ---")
    mock_get.return_value = MockResponse(MOCK_ADZUNA_RESPONSE, 200)

    # Force mock credentials to ensure we don't skip execution
    os.environ["ADZUNA_APP_ID"] = "test_id"
    os.environ["ADZUNA_APP_KEY"] = "test_key"
    
    # Reload config to pickup mocked env (if necessary, though we patch provider below)
    import app.core.config as config
    config.settings.ADZUNA_APP_ID = "test_id"
    config.settings.ADZUNA_APP_KEY = "test_key"

    db = get_supabase_client()
    provider = AdzunaProvider()
    engine = PipelineEngine(db=db, provider=provider)
    
    print("Running Adzuna ingestion engine...")
    metrics = engine.run()
    
    print("\n--- RESULTS ---")
    for k, v in metrics.items():
        print(f"{k}: {v}")
        
    print("\n--- VALIDATION ---")
    assert metrics["records_received"] == 2, f"Expected 2 records received, got {metrics['records_received']}"
    assert metrics["records_rejected"] == 1, f"Expected 1 rejected (missing title), got {metrics['records_rejected']}"
    # Valid = 1, but might be duplicate if already in db.
    assert metrics["records_valid"] + metrics["records_duplicate"] == 1, "Expected 1 valid/duplicate combined"
    print("All assertions passed!")
    
if __name__ == "__main__":
    run_test()
