import requests
import json

print("Testing API endpoints...")
print("-" * 50)

try:
    # Test ping
    r = requests.get("http://127.0.0.1:8000/api/ping", timeout=2)
    print(f"✓ Ping: {r.json()}")
    
    # Test health
    r = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
    data = r.json()
    print(f"✓ Health: CPU={data.get('cpu')}%, RAM={data.get('ram')}%, Healthy={data.get('is_healthy')}")
    
    print("\n✓ API is working correctly!")
except requests.exceptions.ConnectionError:
    print("✗ API not running. Start it with: start_api.bat")
except Exception as e:
    print(f"✗ Error: {e}")
