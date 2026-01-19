import requests

print("Testing backend API...")

# Test health endpoint
try:
    response = requests.get('http://localhost:5000/api/health', timeout=5)
    print(f"✅ Health check: {response.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test leads endpoint
try:
    print("📡 Fetching leads from Facebook (this may take 30-60 seconds)...")
    response = requests.get('http://localhost:5000/api/leads', timeout=120)
    data = response.json()
    print(f"✅ Leads API: {data['count']} leads found")
    if data['count'] > 0:
        print(f"First lead: {data['data'][0].get('name')}")
except Exception as e:
    print(f"❌ Leads API failed: {e}")
