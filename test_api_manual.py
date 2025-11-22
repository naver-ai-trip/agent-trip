"""Manual API testing script for the AI Travel Agent."""

import requests
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
AUTH_TOKEN = "7|SXQRsdEG9gmd0PdtqHfwHegZYSYXqfEbRmPrMwFE63756727"  # Update this with your valid token


def test_health():
    """Test the health endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_chat_basic(session_id: int = 1):
    """Test basic chat without trip context."""
    print("\n" + "="*60)
    print("TEST 2: Basic Chat - Find Places")
    print("="*60)
    
    payload = {
        "session_id": session_id,
        "message": "Find tourist attractions in Seoul",
        "auth_token": AUTH_TOKEN
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    response = requests.post(
        f"{API_BASE_URL}/api/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Message: {result.get('message', '')[:200]}...")
        print(f"Actions Taken: {result.get('actions_taken', [])}")
        print(f"Places Found: {len(result.get('places_found', []))}")
        
        # Show first place if available
        places = result.get('places_found', [])
        if places:
            print(f"\nFirst Place:")
            print(json.dumps(places[0], indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ Error!")
        print(f"Response: {response.text}")
    print()


def test_chat_multilingual(session_id: int = 1):
    """Test chat with Korean query."""
    print("\n" + "="*60)
    print("TEST 3: Multilingual Chat - Korean Query")
    print("="*60)
    
    payload = {
        "session_id": session_id,
        "message": "경복궁 근처 맛집 추천해줘",  # Recommend restaurants near Gyeongbokgung
        "auth_token": AUTH_TOKEN
    }
    
    print(f"Request: {payload['message']}")
    print("\nSending request...")
    
    response = requests.post(
        f"{API_BASE_URL}/api/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Message: {result.get('message', '')[:300]}...")
        print(f"Places Found: {len(result.get('places_found', []))}")
    else:
        print(f"\n❌ Error!")
        print(f"Response: {response.text}")
    print()


def test_chat_trip_planning(session_id: int = 1):
    """Test trip planning functionality."""
    print("\n" + "="*60)
    print("TEST 4: Trip Planning")
    print("="*60)
    
    payload = {
        "session_id": session_id,
        "message": "Plan a 3-day trip to Busan",
        "auth_token": AUTH_TOKEN,
        "trip_id": 1
    }
    
    print(f"Request: {payload['message']}")
    print("\nSending request...")
    
    response = requests.post(
        f"{API_BASE_URL}/api/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Message: {result.get('message', '')[:300]}...")
        print(f"Components: {len(result.get('components', []))}")
        print(f"Next Suggestions: {result.get('next_suggestions', [])}")
    else:
        print(f"\n❌ Error!")
        print(f"Response: {response.text}")
    print()


def test_streaming_chat(session_id: int = 1):
    """Test streaming chat endpoint."""
    print("\n" + "="*60)
    print("TEST 5: Streaming Chat")
    print("="*60)
    
    payload = {
        "session_id": session_id,
        "message": "What are the best places to visit in Jeju Island?",
        "auth_token": AUTH_TOKEN
    }
    
    print(f"Request: {payload['message']}")
    print("\nStreaming response...")
    print("-" * 60)
    
    response = requests.post(
        f"{API_BASE_URL}/api/chat/stream",
        json=payload,
        headers={"Content-Type": "application/json"},
        stream=True
    )
    
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: '):
                    data = decoded[6:]  # Remove 'data: ' prefix
                    if data != '[DONE]':
                        try:
                            chunk = json.loads(data)
                            print(chunk.get('content', ''), end='', flush=True)
                        except json.JSONDecodeError:
                            pass
        print("\n" + "-" * 60)
        print("✅ Streaming completed!")
    else:
        print(f"❌ Error! Status: {response.status_code}")
        print(f"Response: {response.text}")
    print()


def main():
    """Run all API tests."""
    print("\n" + "🚀"*30)
    print("AI TRAVEL AGENT - API TESTING")
    print("🚀"*30)
    print(f"\nAPI Base URL: {API_BASE_URL}")
    print(f"Auth Token: {AUTH_TOKEN[:20]}...")
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Basic chat
        test_chat_basic(session_id=1)
        
        # Test 3: Multilingual
        test_chat_multilingual(session_id=1)
        
        # Test 4: Trip planning
        test_chat_trip_planning(session_id=1)
        
        # Test 5: Streaming (optional - comment out if not needed)
        # test_streaming_chat(session_id=1)
        
        print("\n" + "="*60)
        print("✅ ALL API TESTS COMPLETED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server!")
        print("Make sure the server is running on http://127.0.0.1:8000")
        print("Start server with: uvicorn src.main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
