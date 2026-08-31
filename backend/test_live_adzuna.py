import os
from dotenv import load_dotenv
import requests

# Load from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app_id = os.environ.get("ADZUNA_APP_ID")
app_key = os.environ.get("ADZUNA_APP_KEY")

if not app_id or not app_key:
    print("Keys not found in .env file!")
else:
    print(f"Loaded App ID: {app_id[:4]}...")
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 1,
        "content-type": "application/json"
    }
    
    print("Pinging Adzuna API...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print("SUCCESS! The key is working.")
        print(f"Total jobs found in India: {data.get('count')}")
        if data.get("results"):
            print(f"Sample Job Title: {data['results'][0].get('title')}")
    else:
        print(f"FAILED! Status Code: {response.status_code}")
        print(f"Response: {response.text}")
