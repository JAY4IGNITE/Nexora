import requests

print("Testing Intelligence Endpoints...")

try:
    roles = requests.get("http://localhost:8000/api/v1/intelligence/demand/roles").json()
    print(f"Roles returned: {len(roles)}")
    if roles:
        print(f"Top Role: {roles[0]}")
        
    skills = requests.get("http://localhost:8000/api/v1/intelligence/demand/skills").json()
    print(f"\nSkills returned: {len(skills)}")
    if skills:
        print(f"Top Skill: {skills[0]}")
        
    sectors = requests.get("http://localhost:8000/api/v1/intelligence/demand/sectors").json()
    print(f"\nSectors returned: {len(sectors)}")
    
    geography = requests.get("http://localhost:8000/api/v1/intelligence/demand/geography").json()
    print(f"\nGeography returned: {len(geography)}")
    
    trends = requests.get("http://localhost:8000/api/v1/intelligence/trends/skills").json()
    print(f"\nSkill Trends returned: {len(trends)}")
    if trends:
        print(f"First Trend entry: {trends[0]}")
        
except Exception as e:
    print(f"Failed: {e}")
