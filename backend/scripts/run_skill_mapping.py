import os
import sys

# Ensure backend is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ingestion.skill_mapper import run_skill_mapping
import asyncio
from dotenv import load_dotenv

# Ensure env vars are loaded first!
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))

if __name__ == "__main__":
    asyncio.run(run_skill_mapping())
