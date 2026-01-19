import requests
import time

print("Waiting for backend...")
time.sleep(2)

print("Testing backend API...")
response = requests.get('http://localhost:5000/api/leads', timeout=10)
data = response.json()
print(f"\n🎯 RESULT: {data['count']} leads found")

if data['count'] > 0:
    print(f"\n✅ SUCCESS! First 5 leads:")
    for lead in data['data'][:5]:
        print(f"  - {lead.get('name')} ({lead.get('email')})")
else:
    print(f"\n❌ NO LEADS - Backend can't fetch from database")
