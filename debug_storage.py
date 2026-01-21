#!/usr/bin/env python3
"""
Debug script to check database state and diagnose persistence issues
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

supabase: Client = create_client(url, key)

print("=" * 60)
print("🔍 AUTO DASHBOARD DATABASE DEBUG")
print("=" * 60)

# Check if tables exist
print("\n📋 Checking table existence...")
try:
    # Try to query each table
    tables_to_check = ['clients_data', 'properties_data', 'leads']
    
    for table_name in tables_to_check:
        try:
            result = supabase.table(table_name).select('count', count='exact').execute()
            count = result.count if hasattr(result, 'count') else len(result.data)
            print(f"✅ {table_name}: EXISTS (rows: {count})")
        except Exception as e:
            if 'not found' in str(e).lower() or '42P01' in str(e):
                print(f"❌ {table_name}: DOES NOT EXIST")
            else:
                print(f"⚠️ {table_name}: ERROR - {str(e)[:100]}")

except Exception as e:
    print(f"❌ Error checking tables: {str(e)}")

# Check leads
print("\n👥 Checking leads with email containing 'test'...")
try:
    result = supabase.table('leads').select('id, email, phone, name').limit(10).execute()
    if result.data:
        for lead in result.data:
            if 'test' in str(lead.get('email', '')).lower() or 'test' in str(lead.get('name', '')).lower():
                print(f"  - ID: {lead['id'][:8]}... | Email: {lead.get('email', 'N/A')} | Phone: {lead.get('phone', 'N/A')} | Name: {lead.get('name', 'N/A')}")
    else:
        print("  No test leads found")
except Exception as e:
    print(f"❌ Error querying leads: {str(e)[:100]}")

# Check clients_data
print("\n💾 Checking clients_data entries...")
try:
    result = supabase.table('clients_data').select('*').limit(10).execute()
    if result.data:
        print(f"Found {len(result.data)} entries:")
        for entry in result.data:
            print(f"  - ID: {entry['id'][:8]}... | Lead ID: {entry.get('lead_id', 'NULL')[:8] if entry.get('lead_id') else 'NULL'}... | Email: {entry.get('email', 'N/A')}")
            if entry.get('drivers'):
                print(f"    Drivers data size: {len(str(entry['drivers']))} bytes")
    else:
        print("⚠️ No entries in clients_data table")
except Exception as e:
    if 'not found' in str(e).lower() or '42P01' in str(e):
        print("❌ clients_data table does not exist - SQL migration not run!")
    else:
        print(f"❌ Error querying clients_data: {str(e)[:100]}")

# Check if there are any properties
print("\n🏠 Checking properties_data entries...")
try:
    result = supabase.table('properties_data').select('*').limit(10).execute()
    if result.data:
        print(f"Found {len(result.data)} entries")
    else:
        print("⚠️ No entries in properties_data table")
except Exception as e:
    if 'not found' in str(e).lower() or '42P01' in str(e):
        print("❌ properties_data table does not exist - SQL migration not run!")
    else:
        print(f"❌ Error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("🔧 DIAGNOSIS CHECKLIST:")
print("=" * 60)
print("1. Are clients_data and properties_data tables created?")
print("2. If not, run add_data_tables.sql in Supabase SQL Editor")
print("3. Check if test leads exist in leads table")
print("4. If saved data exists, check lead_id linking")
print("5. Check backend logs when saving for errors")
print("=" * 60)
