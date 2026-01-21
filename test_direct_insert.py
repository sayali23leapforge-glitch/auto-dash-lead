#!/usr/bin/env python3
"""Direct test of database insert"""
import sys
import os
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('.env.local')

from supabase import create_client
url = os.getenv("VITE_SUPABASE_URL")
key = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

print("Testing direct database insert...\n")

# Test 1: Simple insert
print("1️⃣ Test 1: Simple insert")
try:
    data_to_insert = {
        'email': 'direct_test@example.com',
        'phone': '5555555555',
        'drivers': [{'name': 'Test Driver', 'email': 'direct_test@example.com'}]
    }
    result = supabase.table('clients_data').insert(data_to_insert).execute()
    print(f"✅ Insert successful!")
    print(f"   Returned: {result.data}")
except Exception as e:
    print(f"❌ Insert failed: {str(e)}")

# Test 2: Verify it was inserted
print("\n2️⃣ Test 2: Query back the data")
try:
    result = supabase.table('clients_data').select('*').eq('email', 'direct_test@example.com').execute()
    if result.data:
        print(f"✅ Found {len(result.data)} entries!")
        for entry in result.data:
            print(f"   - ID: {entry['id']}")
            print(f"   - Email: {entry['email']}")
            print(f"   - Phone: {entry['phone']}")
    else:
        print(f"❌ No data found!")
except Exception as e:
    print(f"❌ Query failed: {str(e)}")

# Test 3: Check total count
print("\n3️⃣ Test 3: Total table count")
try:
    result = supabase.table('clients_data').select('count', count='exact').execute()
    print(f"✅ Total entries in clients_data: {result.count}")
except Exception as e:
    print(f"❌ Count failed: {str(e)}")
