import requests
import json

print("Quick Backend Test...")
try:
    response = requests.get('http://localhost:5000/api/leads', timeout=120)
    data = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Lead Count: {data.get('count', 0)}")
    if data.get('data'):
        first_lead = data['data'][0]
        print(f"✅ First Lead: {first_lead.get('name')}")
        print(f"   - ID: {first_lead.get('id')}")
        print(f"   - Phone: {first_lead.get('phone')}")
        print(f"   - Email: {first_lead.get('email')}")
        print(f"   - Created: {first_lead.get('created_at')}")
except Exception as e:
    print(f"❌ Error: {e}")
