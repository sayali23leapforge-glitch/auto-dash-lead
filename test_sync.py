import requests
import time

# Wait for backend to start
print("Waiting for backend to start...")
time.sleep(3)

# Test sync endpoint
try:
    print("Calling /api/leads/sync...")
    response = requests.post('http://localhost:5000/api/leads/sync', timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
