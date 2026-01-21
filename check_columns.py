#!/usr/bin/env python3
"""Check what columns exist in clients_data"""
import sys, os
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('.env.local')

from supabase import create_client
url = os.getenv("VITE_SUPABASE_URL")
key = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

print("Checking clients_data table schema...\n")

# Try to insert with minimal fields
try:
    # Try with just email
    result = supabase.table('clients_data').insert({'email': 'test@test.com'}).execute()
    print(f"✅ Insert with just 'email' works")
    print(f"   Columns that worked: email")
except Exception as e:
    print(f"❌ Insert with 'email' failed: {str(e)[:100]}")

try:
    # Try with email + drivers
    result = supabase.table('clients_data').insert({
        'email': 'test2@test.com',
        'drivers': []
    }).execute()
    print(f"✅ Insert with 'email' + 'drivers' works")
except Exception as e:
    print(f"❌ Insert with 'email' + 'drivers' failed: {str(e)[:100]}")

try:
    # Try with email + lead_id
    result = supabase.table('clients_data').insert({
        'email': 'test3@test.com',
        'lead_id': 'some-uuid'
    }).execute()
    print(f"✅ Insert with 'email' + 'lead_id' works")
except Exception as e:
    print(f"❌ Insert with 'email' + 'lead_id' failed: {str(e)[:100]}")

print("\n📋 Attempting to select from table to infer schema...")
try:
    result = supabase.table('clients_data').select('*').limit(1).execute()
    if result.data:
        print(f"✅ Got data:")
        print(f"   Columns: {list(result.data[0].keys())}")
    else:
        # Try empty select to see schema
        result2 = supabase.table('clients_data').select().limit(0).execute()
        print(f"Empty select result: {result2}")
except Exception as e:
    print(f"Error: {str(e)[:200]}")

print("\n💡 Likely the 'phone' and 'name' columns don't exist.")
print("   Need to check/modify the SQL migration or update the backend code.")
