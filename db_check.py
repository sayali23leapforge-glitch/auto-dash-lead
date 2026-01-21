#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'backend')

# Load env from .env.local
from dotenv import load_dotenv
load_dotenv('.env.local')

from supabase import create_client
url = os.getenv("VITE_SUPABASE_URL")
key = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Missing env vars")
    print(f"   URL: {url}")
    print(f"   KEY: {key}")
    sys.exit(1)

supabase = create_client(url, key)

print("=" * 60)
print("🔍 DATABASE STATE CHECK")
print("=" * 60)

# Check table exists
try:
    result = supabase.table('clients_data').select('count', count='exact').execute()
    print(f"✅ clients_data table EXISTS")
    print(f"   Total entries: {result.count}")
except Exception as e:
    if 'not found' in str(e).lower() or '42P01' in str(e):
        print(f"❌ clients_data table DOES NOT EXIST")
        print(f"   You need to run: add_data_tables.sql in Supabase")
    else:
        print(f"⚠️  Error: {str(e)}")

# Check for test data
try:
    result = supabase.table('clients_data').select('email, id').execute()
    if result.data:
        print(f"\n📊 Entries in clients_data:")
        for entry in result.data:
            print(f"   - {entry['email']}")
    else:
        print(f"\n⚠️  clients_data table is EMPTY - No saved data found")
except Exception as e:
    print(f"Error querying: {str(e)[:100]}")

# Check leads table
try:
    result = supabase.table('leads').select('count', count='exact').execute()
    print(f"\n👥 leads table: {result.count} entries")
except Exception as e:
    print(f"Error checking leads: {str(e)}")

print("=" * 60)
