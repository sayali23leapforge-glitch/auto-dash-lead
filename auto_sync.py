"""
Auto-sync Facebook leads to database every 2 minutes
Run this in background to keep database updated
"""
import time
import requests

SYNC_INTERVAL = 120  # 2 minutes

print("🔄 Auto-sync started - syncing Facebook leads every 2 minutes")
print("Press Ctrl+C to stop")

while True:
    try:
        print(f"\n⏰ {time.strftime('%H:%M:%S')} - Syncing leads from Facebook...")
        response = requests.post('http://localhost:5000/api/leads/sync', timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sync complete: {data.get('message')}")
        else:
            print(f"❌ Sync failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"💤 Sleeping for {SYNC_INTERVAL} seconds...")
    time.sleep(SYNC_INTERVAL)
