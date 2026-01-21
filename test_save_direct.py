#!/usr/bin/env python3
"""Direct test of save endpoint"""
import requests
import json
import time

# Start server
import subprocess
import sys

print("Starting server...")
server_process = subprocess.Popen([sys.executable, "backend/app.py"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
time.sleep(4)

try:
    BASE_URL = "http://127.0.0.1:5000"

    test_data = {
        "id": "direct_test_123@gmail.com",
        "created_at": "2026-01-21T20:00:00.000Z",
        "updated_at": "2026-01-21T20:00:00.000Z",
        "drivers": [
            {
                "id": 1,
                "mainName": "DIRECT TEST",
                "mainRel": "Principal",
                "personalName": "DIRECT TEST",
                "personalAddress": "456 Direct St",
                "personalDob": "02/02/1990",
                "personalMobile": "4444444444",
                "personalEmail": "direct_test_123@gmail.com",
                "licRenewal": "01/21/2027",
                "licNumber": "DIRECT999"
            }
        ]
    }

    print("\n" + "="*60)
    print("Testing /api/save-client endpoint")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/api/save-client",
        json=test_data,
        timeout=5
    )
    
    print(f"OK Response Status: {response.status_code}")
    resp_json = response.json()
    print(f"Response JSON:")
    print(json.dumps(resp_json, indent=2))

    # Check database
    print("\n" + "="*60)
    print("Checking database...")
    print("="*60)

    import sys
    sys.path.insert(0, 'backend')
    from dotenv import load_dotenv
    import os
    load_dotenv('.env.local')

    from supabase import create_client
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    result = supabase.table('clients_data').select('count', count='exact').execute()
    print(f"Total clients_data entries: {result.count}")

    result = supabase.table('clients_data').select('*').eq('email', 'direct_test_123@gmail.com').execute()
    if result.data:
        print(f"SUCCESS: Found {len(result.data)} entry!")
        for entry in result.data:
            print(f"   ID: {entry['id']}")
            print(f"   Email: {entry['email']}")
            print(f"   Drivers: {len(entry.get('drivers', []))} drivers")
            if entry.get('drivers'):
                print(f"   First driver: {entry['drivers'][0].get('personalName')}")
    else:
        print(f"FAIL: Data NOT found in database!")

finally:
    print("\nShutting down server...")
    server_process.terminate()
    server_process.wait(timeout=2)
