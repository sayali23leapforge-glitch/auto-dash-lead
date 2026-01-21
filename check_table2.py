#!/usr/bin/env python3
import sys
import os

# Add backend to path
sys.path.insert(0, 'D:\\Auto dashboard\\backend')

from app import supabase
import json

print("🔍 Checking clients_data table...")
try:
    # Try to query the table
    result = supabase.table('clients_data').select('*').limit(1).execute()
    print(f"✅ Table EXISTS! Found {len(result.data)} entries")
    if result.data:
        print(f"Sample entry: {json.dumps(result.data[0], indent=2, default=str)[:300]}...")
except Exception as e:
    error_str = str(e)
    if 'not found' in error_str.lower() or '42P01' in error_str:
        print(f"❌ TABLE DOES NOT EXIST - Error: {error_str}")
        print(f"   Need to run: add_data_tables.sql in Supabase SQL Editor")
    else:
        print(f"❌ Error: {error_str[:300]}")
        import traceback
        traceback.print_exc()

print("\n📊 Checking all clients_data entries...")
try:
    result = supabase.table('clients_data').select('email, id, created_at').execute()
    print(f"Total entries: {len(result.data)}")
    for entry in result.data[:5]:
        print(f"  - Email: {entry.get('email')}, Created: {entry.get('created_at')}")
except Exception as e:
    print(f"Error: {str(e)[:200]}")

print("\n🔍 Looking for test data with email 'test@123gmail.com'...")
try:
    result = supabase.table('clients_data').select('*').eq('email', 'test@123gmail.com').execute()
    if result.data:
        print(f"✅ FOUND {len(result.data)} entries!")
        for entry in result.data:
            print(f"   - ID: {entry.get('id')}")
            print(f"   - Lead ID: {entry.get('lead_id')}")
            print(f"   - Email: {entry.get('email')}")
            if entry.get('drivers'):
                print(f"   - Drivers data size: {len(str(entry['drivers']))} bytes")
    else:
        print(f"❌ No entries found for test@123gmail.com")
except Exception as e:
    print(f"❌ Error searching: {str(e)[:200]}")
