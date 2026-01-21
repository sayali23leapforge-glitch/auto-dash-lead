#!/usr/bin/env python3
"""Insert complete test data with vehicles and claims"""
import sys, os
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('.env.local')

from supabase import create_client
import json
from datetime import datetime

url = os.getenv("VITE_SUPABASE_URL")
key = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

# Test data with ALL fields including vehicles and claims
test_data = {
    'email': 'complete_test@example.com',
    'drivers': [
        {
            'id': 1,
            'mainName': 'COMPLETE TEST',
            'mainRel': 'Principal',
            'personalName': 'COMPLETE TEST',
            'personalAddress': '789 Complete St, City, ON M1M 1M1',
            'personalDob': '05/15/1985',
            'personalMobile': '9876543210',
            'personalEmail': 'complete_test@example.com',
            'licRenewal': '05/15/2027',
            'licNumber': 'COMP123456',
            'licClass': 'G',
            'licStatus': 'Valid',
            'licIssue': '05/15/2017',
            'demPoints': '0',
            
            # Insurance details from DASH
            'issueDate': '11/20/2025',
            'reportDate': '11/20/2025',
            'yearsInsurance': '5',
            'firstInsDate': '12/16/2019',
            'policyStart': '12/16/2023',
            'policyEnd': '12/16/2025',
            
            # Gap calculation
            'gapStart': '12/16/2019',
            'gapEnd': '12/16/2025',
            
            # Vehicles
            'vehicles': [
                {
                    'vin': '2HKRS4H5XRH104391',
                    'yearMake': '2024 HONDA CR-V',
                    'make': 'HONDA',
                    'model': 'CR-V',
                    'year': '2024'
                }
            ],
            
            # Claims
            'claims': [
                {
                    'claimNumber': 'CLM-001',
                    'claimType': 'Collision',
                    'claimDate': '2024-03-15',
                    'claimAmount': '5000',
                    'status': 'Settled'
                }
            ]
        }
    ]
}

print("Inserting complete test data with vehicles and claims...")
try:
    result = supabase.table('clients_data').insert(test_data).execute()
    print(f"SUCCESS: Inserted data with ID: {result.data[0]['id']}")
    print(f"Email: {result.data[0]['email']}")
    print(f"Drivers: {len(result.data[0]['drivers'])} driver(s)")
    driver = result.data[0]['drivers'][0]
    print(f"Vehicles: {len(driver.get('vehicles', []))} vehicle(s)")
    print(f"Claims: {len(driver.get('claims', []))} claim(s)")
except Exception as e:
    print(f"Error: {str(e)}")

print("\nNow open browser at:")
print("http://localhost:5000/Auto%20dashboard.html?name=COMPLETE%20TEST&phone=9876543210&email=complete_test@example.com")
