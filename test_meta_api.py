import requests
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('.env.local')

META_API_VERSION = 'v18.0'
META_LEAD_FORM_ID = os.getenv('META_LEAD_FORM_ID')
META_PAGE_ACCESS_TOKEN = os.getenv('META_PAGE_ACCESS_TOKEN')

print(f"Testing Meta API...")
print(f"Lead Form ID: {META_LEAD_FORM_ID}")
print(f"Access Token: {META_PAGE_ACCESS_TOKEN[:20]}...{META_PAGE_ACCESS_TOKEN[-10:]}")
print()

# Test API call
url = f'https://graph.facebook.com/{META_API_VERSION}/{META_LEAD_FORM_ID}/leads'
params = {
    'fields': 'id,created_time,field_data,adgroup_id',
    'access_token': META_PAGE_ACCESS_TOKEN,
    'limit': 10
}

print(f"Calling: {url}")
response = requests.get(url, params=params)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nTotal leads found: {len(data.get('data', []))}")
    if data.get('data'):
        print(f"First lead: {data['data'][0]}")
else:
    print(f"\nERROR: {response.json()}")
