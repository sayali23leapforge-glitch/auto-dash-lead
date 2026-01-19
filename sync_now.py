import os
import requests
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv('.env.local')

META_API_VERSION = 'v18.0'
META_LEAD_FORM_ID = os.getenv('META_LEAD_FORM_ID')
META_PAGE_ACCESS_TOKEN = os.getenv('META_PAGE_ACCESS_TOKEN')
SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SERVICE_ROLE_KEY')

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🚀 Starting Facebook to Supabase sync...")

# Fetch from Facebook
url = f'https://graph.facebook.com/{META_API_VERSION}/{META_LEAD_FORM_ID}/leads'
params = {
    'fields': 'id,created_time,field_data',
    'access_token': META_PAGE_ACCESS_TOKEN,
    'limit': 50
}

response = requests.get(url, params=params)
data = response.json()
facebook_leads = data.get('data', [])

print(f"📥 Fetched {len(facebook_leads)} leads from Facebook")

# Parse and save to Supabase
saved_count = 0
for lead in facebook_leads:
    field_data = lead.get('field_data', [])
    
    # Parse fields
    lead_dict = {}
    for field in field_data:
        name = field.get('name')
        values = field.get('values', [])
        if values and len(values) > 0:
            if name == 'full_name':
                lead_dict['name'] = values[0]
            elif name == 'email':
                lead_dict['email'] = values[0]
            elif name == 'phone':
                lead_dict['phone'] = values[0]
    
    # Create lead object for Supabase
    supabase_lead = {
        'meta_lead_id': lead.get('id'),
        'name': lead_dict.get('name', 'Unknown'),
        'email': lead_dict.get('email'),
        'phone': lead_dict.get('phone'),
        'type': 'general',
        'status': 'New Lead',
        'is_manual': False,
        'created_at': lead.get('created_time')
    }
    
    try:
        # Insert into Supabase
        result = supabase.table('leads').insert(supabase_lead).execute()
        if result.data:
            saved_count += 1
            print(f"✅ Saved: {supabase_lead['name']}")
    except Exception as e:
        if 'duplicate' in str(e).lower():
            print(f"⏭️  Skipped (duplicate): {supabase_lead['name']}")
        else:
            print(f"❌ Error saving {supabase_lead['name']}: {e}")

print(f"\n🎉 Sync complete! Saved {saved_count} new leads to Supabase")
