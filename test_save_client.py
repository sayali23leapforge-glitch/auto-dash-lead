#!/usr/bin/env python3
"""Test the save-client endpoint"""

import requests
import json

# Sample data that matches what frontend sends
test_data = {
    "id": "test@123gmail.com",
    "created_at": "2026-01-21T12:09:03.960Z",
    "updated_at": "2026-01-21T12:09:03.966Z",
    "drivers": [
        {
            "id": 1,
            "mainName": "KURIAKOSE, MANI",
            "mainRel": "Principal",
            "personalName": "KURIAKOSE, MANI",
            "personalAddress": "104 4 GLENBROOK DR GUELPH ON N1E1A9",
            "personalDob": "03/31/1976",
            "personalMobile": "8080603212",
            "personalEmail": "test@123gmail.com",
            "licRenewal": "11/20/2025",
            "licNumber": "K9365-51607-60331",
            "mvrExpiry": "03/31/2029",
            "mvrDob": "03/31/1976",
            "mvrIssue": "02/18/1997",
            "mvrStatus": "Valid",
            "mvrDemerits": "00",
            "mvrClass": "G",
            "mvrConditions": "*/N",
            "mvrConvictions": "0",
            "claims": [],
            "vehicles": []
        }
    ]
}

print("🧪 Testing /api/save-client endpoint...")
print(f"📦 Sending {len(test_data['drivers'])} driver(s)")

try:
    response = requests.post('http://localhost:5000/api/save-client', json=test_data)
    print(f"\n📍 Status: {response.status_code}")
    print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Now try to retrieve it
print("\n🔍 Testing /api/get-client-data/test@123gmail.com...")
try:
    response = requests.get('http://localhost:5000/api/get-client-data/test@123gmail.com')
    print(f"📍 Status: {response.status_code}")
    print(f"📄 Response: {json.dumps(response.json(), indent=2)[:500]}...")
except Exception as e:
    print(f"❌ Error: {str(e)}")
