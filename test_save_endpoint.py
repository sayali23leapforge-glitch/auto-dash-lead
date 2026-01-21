#!/usr/bin/env python3
"""Test the /api/save-client endpoint"""
import requests
import json

# Wait a moment for server to be ready
import time
time.sleep(2)

BASE_URL = "http://localhost:5000"

# Test data matching what the frontend sends
test_data = {
    "id": "test_debug_123@gmail.com",
    "created_at": "2026-01-21T18:00:00.000Z",
    "updated_at": "2026-01-21T18:00:00.000Z",
    "drivers": [
        {
            "id": 1,
            "mainName": "TEST DRIVER",
            "mainRel": "Principal",
            "personalName": "TEST DRIVER",
            "personalAddress": "123 Test St",
            "personalDob": "01/01/1990",
            "personalMobile": "9999999999",
            "personalEmail": "test_debug_123@gmail.com",
            "licRenewal": "01/21/2026",
            "licNumber": "TEST123",
            "licClass": "G",
            "licStatus": "Valid",
            "licIssue": "01/01/2020",
            "demPoints": "0"
        }
    ]
}

print("=" * 60)
print("📤 Testing /api/save-client endpoint")
print("=" * 60)
print(f"Sending: {json.dumps(test_data, indent=2)[:200]}...")
print()

try:
    response = requests.post(
        f"{BASE_URL}/api/save-client",
        json=test_data,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("=" * 60)
print("Checking database...")
print("=" * 60)

# Now check if data was saved
import sys
sys.path.insert(0, 'backend')
from dotenv import load_dotenv
import os
load_dotenv('.env.local')

from supabase import create_client
url = os.getenv("VITE_SUPABASE_URL")
key = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

try:
    result = supabase.table('clients_data').select('*').eq('email', 'test_debug_123@gmail.com').execute()
    if result.data:
        print(f"✅ Found {len(result.data)} entries!")
        for entry in result.data:
            print(f"   ID: {entry['id']}")
            print(f"   Email: {entry['email']}")
            print(f"   Phone: {entry.get('phone')}")
            print(f"   Drivers: {len(entry.get('drivers', []))} drivers")
    else:
        print(f"❌ No entries found for test_debug_123@gmail.com")
except Exception as e:
    print(f"❌ Query error: {str(e)}")
