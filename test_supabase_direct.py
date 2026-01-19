from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SERVICE_ROLE_KEY')

print(f"Connecting to: {SUPABASE_URL}")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Query leads table
try:
    response = supabase.table('leads').select('*').limit(5).execute()
    print(f"\n✅ Found {len(response.data)} leads in database:")
    for lead in response.data:
        print(f"  - {lead.get('name')} (ID: {lead.get('id')})")
except Exception as e:
    print(f"\n❌ Error querying database: {e}")
