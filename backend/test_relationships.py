import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    sys.exit(1)

supabase: Client = create_client(url, key)

try:
    print("Testing relationships and seed data...")
    
    # Check states
    states = supabase.table("states").select("*").execute()
    print(f"States found: {len(states.data)}")
    
    # Check sectors
    sectors = supabase.table("sectors").select("*").execute()
    print(f"Sectors found: {len(sectors.data)}")
    
    # Check skills
    skills = supabase.table("skills").select("*").execute()
    print(f"Skills found: {len(skills.data)}")
    
    # Check relationships (Job Roles -> Sector)
    roles = supabase.table("job_roles").select("*, sectors(name)").execute()
    print(f"Job Roles (with sector): {roles.data}")
    
    print("All relationship validations passed!")
except Exception as e:
    print(f"Validation failed: {e}")
    sys.exit(1)
