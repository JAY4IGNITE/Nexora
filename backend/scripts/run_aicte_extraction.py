import os
import sys
from dotenv import load_dotenv

# Ensure env vars are loaded first!
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))

# Ensure backend is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ingestion.aicte_pipeline import run_pipeline
import asyncio

if __name__ == "__main__":
    asyncio.run(run_pipeline())
