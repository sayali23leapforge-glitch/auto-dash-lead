#!/usr/bin/env python3
"""Check if clients_data table exists in Supabase"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

print("🔍 Checking clients_data table...")
try:
    # Try to query the table
    result = supabase.table('clients_data').select('*').limit(1).execute()
    print(f"✅ Table EXISTS! Found {len(result.data)} entries")
    if result.data:
        print(f"Sample entry: {json.dumps(result.data[0], indent=2, default=str)[:200]}...")
except Exception as e:
    error_str = str(e)
    if 'not found' in error_str.lower() or '42P01' in error_str:
        print(f"❌ TABLE DOES NOT EXIST")
        print(f"   You must run the SQL migration in Supabase")
        print(f"   SQL file location: add_data_tables.sql")
    else:
        print(f"❌ Error: {error_str[:200]}")

print("\n🔍 Checking if we can insert test data...")
try:
    test_insert = supabase.table('clients_data').insert({
        'email': 'test_debug@example.com',
        'drivers': [{'test': 'data'}]
    }).execute()
    print(f"✅ Insert works! Inserted with ID: {test_insert.data[0]['id'] if test_insert.data else 'unknown'}")
    
    # Try to retrieve it
    test_retrieve = supabase.table('clients_data').select('*').eq('email', 'test_debug@example.com').execute()
    print(f"✅ Retrieved: {len(test_retrieve.data)} entries")
    if test_retrieve.data:
        print(f"   Data: {json.dumps(test_retrieve.data[0], indent=2, default=str)[:300]}...")
except Exception as e:
    print(f"❌ Error: {str(e)[:200]}")
