#!/usr/bin/env python3
"""Test both save and retrieve endpoints"""
import requests
import json
import time
import subprocess
import sys

# Start server
print("Starting server...")
server_process = subprocess.Popen([sys.executable, "backend/app.py"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
time.sleep(4)

try:
    BASE_URL = "http://127.0.0.1:5000"

    # First save some test data
    test_data = {
        "id": "retrieve_test@gmail.com",
        "drivers": [
            {
                "id": 1,
                "personalName": "RETRIEVE TEST",
                "personalEmail": "retrieve_test@gmail.com",
                "personalMobile": "7777777777",
                "licNumber": "RET123",
                "licRenewal": "03/21/2027"
            }
        ]
    }

    print("Step 1: Saving client data...")
    response = requests.post(f"{BASE_URL}/api/save-client", json=test_data, timeout=5)
    print(f"   Save status: {response.status_code}")
    save_result = response.json()
    print(f"   Response: {json.dumps(save_result, indent=2)}")

    # Now retrieve it
    print("\nStep 2: Retrieving client data...")
    response = requests.get(f"{BASE_URL}/api/get-client-data/retrieve_test@gmail.com", timeout=5)
    print(f"   Retrieve status: {response.status_code}")
    retrieve_result = response.json()
    
    if response.status_code == 200 and retrieve_result.get('success'):
        print(f"   SUCCESS!")
        data = retrieve_result.get('data', {})
        print(f"   Email: {data.get('email')}")
        print(f"   Drivers: {len(data.get('drivers', []))} drivers")
        if data.get('drivers'):
            print(f"   Driver name: {data['drivers'][0].get('personalName')}")
    else:
        print(f"   FAILED: {json.dumps(retrieve_result, indent=2)}")

finally:
    print("\nShutting down server...")
    server_process.terminate()
    server_process.wait(timeout=2)
