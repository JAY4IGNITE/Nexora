import logging
import requests
from datetime import datetime
from typing import Generator, Optional
from app.core.config import settings
from app.models.ingestion import RawJobRecord
from app.services.ingestion.provider import JobDataProvider

logger = logging.getLogger(__name__)

class AdzunaProvider(JobDataProvider):
    """
    Ingestion provider for the Adzuna API targeting the India (IN) region.
    """
    def __init__(self, 
                 keyword: str = "", 
                 location: str = "", 
                 category: str = "", 
                 results_per_page: int = 50, 
                 page: int = 1):
        self.app_id = settings.ADZUNA_APP_ID
        self.app_key = settings.ADZUNA_APP_KEY
        
        self.keyword = keyword
        self.location = location
        self.category = category
        self.results_per_page = results_per_page
        self.page = page
        self.base_url = "https://api.adzuna.com/v1/api/jobs/in/search"

    def get_provider_name(self) -> str:
        return "ADZUNA_API"

    def fetch_jobs(self) -> Generator[RawJobRecord, None, None]:
        if not self.app_id or not self.app_key:
            logger.error("Adzuna credentials not configured. Aborting ingestion.")
            return

        url = f"{self.base_url}/{self.page}"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": self.results_per_page,
            "what": self.keyword,
            "where": self.location,
            "category": self.category,
            "content-type": "application/json"
        }
        
        # Remove empty params
        params = {k: v for k, v in params.items() if v}

        try:
            logger.info(f"Fetching Adzuna jobs page {self.page} (limit: {self.results_per_page})")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Adzuna API request failed: {e}")
            return
            
        results = data.get("results", [])
        if not results:
            logger.info("Adzuna API returned empty results.")
            return

        now = datetime.utcnow()

        for job in results:
            try:
                # Extract locations properly (Adzuna returns an area array)
                area = job.get("location", {}).get("area", [])
                city = area[2] if len(area) > 2 else None
                state = area[1] if len(area) > 1 else None
                country = area[0] if len(area) > 0 else None
                
                # Format full location string for fallback mapping
                loc_str = ", ".join([a for a in reversed(area) if a])
                
                # Handle dates
                created = job.get("created")
                posted_dt = datetime.fromisoformat(created.replace("Z", "+00:00")).replace(tzinfo=None) if created else now

                record = RawJobRecord(
                    source="adzuna",
                    source_job_id=str(job.get("id")),
                    source_url=job.get("redirect_url"),
                    title=job.get("title", ""),
                    employer=job.get("company", {}).get("display_name", "Unknown"),
                    description=job.get("description", ""),
                    location=loc_str,
                    state=state,
                    district=city, # Usually Adzuna city maps to our district conceptually
                    city=city,
                    employment_type=job.get("contract_type"),
                    salary_min=job.get("salary_min"),
                    salary_max=job.get("salary_max"),
                    contract_time=job.get("contract_time"),
                    posted_at=posted_dt,
                    collected_at=now
                )
                yield record
            except Exception as e:
                logger.warning(f"Failed to parse Adzuna record {job.get('id')}: {e}")
                continue
