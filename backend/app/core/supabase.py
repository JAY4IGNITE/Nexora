from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    url = settings.SUPABASE_URL
    # For backend auth/admin operations, we use a service role key if available, else anon key
    # If no config is available (e.g. tests), return a mock or None
    if not url:
        logger.warning("SUPABASE_URL not configured.")
        return None
        
    key = settings.SUPABASE_SERVICE_ROLE_KEY if hasattr(settings, "SUPABASE_SERVICE_ROLE_KEY") else None
    if not key:
        logger.warning("SUPABASE_SERVICE_ROLE_KEY not configured, using mock/anon.")
        key = "dummy_key"
        
    return create_client(url, key)

supabase_client = get_supabase_client()
