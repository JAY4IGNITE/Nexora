from abc import ABC, abstractmethod
from typing import List, Generator
from datetime import datetime
from app.models.ingestion import RawJobRecord

class JobDataProvider(ABC):
    """Abstract base class for job data ingestion providers."""
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
        
    @abstractmethod
    def fetch_jobs(self) -> Generator[RawJobRecord, None, None]:
        """Yields raw job records from the external source."""
        pass


class MockJobProvider(JobDataProvider):
    """A deterministic mock provider generating a synthetic dataset for testing."""
    
    def get_provider_name(self) -> str:
        return "MOCK_DEVELOPMENT_DATASET"
        
    def fetch_jobs(self) -> Generator[RawJobRecord, None, None]:
        now = datetime.utcnow()
        
        jobs = [
            {
                "source": "MockBoard",
                "source_job_id": "MOCK-001",
                "title": "Software Engineer",
                "employer": "Tech Corp Pvt Ltd",
                "description": "We need a strong backend engineer who knows Python, SQL, and Docker.",
                "location": "Pune, MH",
                "state": "Maharashtra",
                "district": "Pune",
                "employment_type": "Full Time",
                "experience_requirement": "2-4 years",
                "posted_at": now,
                "collected_at": now,
            },
            {
                "source": "MockBoard",
                "source_job_id": "MOCK-002",
                "title": "Cloud Ops Eng",
                "employer": "CloudSync",
                "description": "Looking for AWS and Kubernetes experts.",
                "location": "Mumbai",
                "state": "Maharashtra",
                "district": "Mumbai City",
                "employment_type": "Contract",
                "experience_requirement": "5+ years",
                "posted_at": now,
                "collected_at": now,
            },
            {
                "source": "MockBoard",
                "source_job_id": "MOCK-003",
                "title": "  Data Analyst  ", # Needs cleaning
                "employer": "DataWiz",
                "description": "Analyze data with SQL and Python.",
                "location": "Bangalore",
                "state": "Karnataka",
                "district": "Bengaluru",
                "employment_type": "FULL-TIME",
                "posted_at": now,
                "collected_at": now,
            },
            {
                # Duplicate of MOCK-001 to test idempotency
                "source": "MockBoard",
                "source_job_id": "MOCK-001",
                "title": "Software Engineer",
                "employer": "Tech Corp Pvt Ltd",
                "description": "We need a strong backend engineer who knows Python, SQL, and Docker.",
                "location": "Pune, MH",
                "posted_at": now,
                "collected_at": now,
            },
            {
                # Missing required fields to test rejection (missing title)
                "source": "MockBoard",
                "source_job_id": "MOCK-004",
                "title": "",
                "employer": "NoTitle Co",
                "description": "Empty title job",
                "collected_at": now,
            },
            {
                # Uses a strange job title to trigger LLM semantic mapping
                "source": "MockBoard",
                "source_job_id": "MOCK-005",
                "title": "Data Ninja and Visualization Guru",
                "employer": "Analytics Hub",
                "description": "Expert in Tableau and SQL to make sense of numbers. Strong communication skills required.",
                "location": "New Delhi",
                "state": "Delhi",
                "district": "New Delhi",
                "employment_type": "FULL_TIME",
                "posted_at": now,
                "collected_at": now,
            }
        ]
        
        for job in jobs:
            try:
                yield RawJobRecord(**job)
            except Exception as e:
                # If validation fails immediately in Pydantic, we just skip yielding 
                # (in a real pipeline we might track this, but the Pipeline engine handles most of it)
                pass
