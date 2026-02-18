"""Debug the 500 error from chatbot API"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("Debugging Chatbot 500 Error")
print("=" * 70)

# Test the exact payload that frontend sends
test_payload = {
    "userId": "user_123",
    "message": "Hello!"
}

print(f"\n📤 Sending request to: {BASE_URL}/api/chatbot/chat")
print(f"📦 Payload: {json.dumps(test_payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/api/chatbot/chat",
        json=test_payload,
        timeout=30
    )
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📝 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"\n✅ Success!")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"\n❌ Error {response.status_code}")
        print(f"Response Text: {response.text}")
        
        try:
            error_data = response.json()
            print(f"Error JSON: {json.dumps(error_data, indent=2)}")
        except:
            pass
            
except requests.exceptions.ConnectionError:
    print(f"\n❌ Connection Error!")
    print(f"Backend is not running at {BASE_URL}")
    print(f"\nPlease start the backend with:")
    print(f"  .\\start-backend.ps1")
    
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
