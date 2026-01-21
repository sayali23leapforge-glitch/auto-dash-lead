"""
Quick database verification script
Checks:
1. Manual leads in 'clients' table
2. Facebook leads in 'leads' table
3. Total counts and data samples
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.local'))

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Supabase credentials not found in .env.local")
    exit(1)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 70)
print("DATABASE VERIFICATION REPORT")
print("=" * 70)

# ========== CHECK LEADS TABLE (Facebook leads) ==========
print("\n1. FACEBOOK LEADS (leads table)")
print("-" * 70)
try:
    leads_response = supabase.table('leads').select('id, name, email, phone, created_at, meta_lead_id, is_manual, status').order('created_at', desc=True).limit(10).execute()
    leads = leads_response.data if leads_response.data else []
    
    # Total count
    total_response = supabase.table('leads').select('id', count='exact').execute()
    total_count = total_response.count if hasattr(total_response, 'count') else len(total_response.data) if total_response.data else 0
    
    print(f"Total leads in database: {total_count}")
    print(f"Recent leads (latest 10):")
    print()
    
    if leads:
        for i, lead in enumerate(leads, 1):
            print(f"  {i}. {lead.get('name', 'N/A')} | {lead.get('email', 'N/A')} | {lead.get('phone', 'N/A')}")
            print(f"     ID: {lead.get('id')} | Meta ID: {lead.get('meta_lead_id')} | Status: {lead.get('status')}")
            print(f"     Created: {lead.get('created_at')} | Manual: {lead.get('is_manual')}")
            print()
    else:
        print("  (No leads found)")
    
    # Count by type
    print("\nBreakdown:")
    facebook_leads = supabase.table('leads').select('id', count='exact').eq('meta_lead_id', None, negate=True).execute()
    facebook_count = facebook_leads.count if hasattr(facebook_leads, 'count') else 0
    print(f"  Facebook leads: {facebook_count}")
    
    manual_leads = supabase.table('leads').select('id', count='exact').eq('is_manual', True).execute()
    manual_count = manual_leads.count if hasattr(manual_leads, 'count') else 0
    print(f"  Manual leads: {manual_count}")
    
except Exception as e:
    print(f"ERROR fetching leads: {str(e)}")

# ========== CHECK CLIENTS TABLE (Manual entries) ==========
print("\n" + "=" * 70)
print("2. CLIENTS TABLE (Manual client data)")
print("-" * 70)
try:
    clients_response = supabase.table('clients').select('*').order('created_at', desc=True).limit(10).execute()
    clients = clients_response.data if clients_response.data else []
    
    # Total count
    total_clients_response = supabase.table('clients').select('id', count='exact').execute()
    total_clients_count = total_clients_response.count if hasattr(total_clients_response, 'count') else len(total_clients_response.data) if total_clients_response.data else 0
    
    print(f"Total clients in database: {total_clients_count}")
    print(f"Recent clients (latest 10):")
    print()
    
    if clients:
        for i, client in enumerate(clients, 1):
            print(f"  {i}. {client.get('name', 'N/A')}")
            print(f"     Email: {client.get('email')} | Phone: {client.get('phone')}")
            print(f"     ID: {client.get('id')}")
            if client.get('created_at'):
                print(f"     Created: {client.get('created_at')}")
            print()
    else:
        print("  (No clients found)")
        
except Exception as e:
    print(f"ERROR fetching clients: {str(e)}")

# ========== SUMMARY ==========
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Facebook leads: {facebook_count}")
print(f"Manual leads: {manual_count}")
print(f"Clients: {total_clients_count}")
print("\n✅ Database check complete!")
