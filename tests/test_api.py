"""Comprehensive test suite for AI Travel Agent API endpoints."""

import asyncio
import httpx
from typing import Dict, Any
import json


# Test configuration
BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "6|Aui9tCjVgJ8U4CJ9VUaP8yVpcP82d4wgQoJhbU529b1f8e9f"
SESSION_ID = 1
TRIP_ID = 1


class AgentTester:
    """Test class for AI Travel Agent endpoints."""
    
    def __init__(self, base_url: str = BASE_URL, auth_token: str = AUTH_TOKEN):
        self.base_url = base_url
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def test_health(self) -> Dict[str, Any]:
        """Test health endpoint."""
        print("\n" + "="*60)
        print("TEST 1: Health Check")
        print("="*60)
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response: {json.dumps(result, indent=2)}")
            return result
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            raise
    
    async def test_chat_basic(self, session_id: int = SESSION_ID) -> Dict[str, Any]:
        """Test basic chat endpoint."""
        print("\n" + "="*60)
        print("TEST 2: Basic Chat - Tourist Attractions")
        print("="*60)
        
        payload = {
            "session_id": session_id,
            "message": "Find tourist attractions in Seoul",
            "auth_token": self.auth_token
        }
        
        print(f"📤 Request: {json.dumps(payload, indent=2)}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")
            
            return result
        except Exception as e:
            print(f"❌ Chat request failed: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise
    
    async def test_chat_with_trip(
        self, 
        session_id: int = SESSION_ID,
        trip_id: int = TRIP_ID
    ) -> Dict[str, Any]:
        """Test chat with trip context."""
        print("\n" + "="*60)
        print("TEST 3: Chat with Trip Context")
        print("="*60)
        
        payload = {
            "session_id": session_id,
            "trip_id": trip_id,
            "message": "Show me hotels near Gangnam",
            "auth_token": self.auth_token
        }
        
        print(f"📤 Request: {json.dumps(payload, indent=2)}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")
            
            return result
        except Exception as e:
            print(f"❌ Chat with trip failed: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise
    
    async def test_multilingual(self, session_id: int = SESSION_ID) -> Dict[str, Any]:
        """Test multilingual support."""
        print("\n" + "="*60)
        print("TEST 4: Multilingual Support (Korean)")
        print("="*60)
        
        payload = {
            "session_id": session_id,
            "message": "부산에서 맛집 추천해줘",  # "Recommend restaurants in Busan"
            "auth_token": self.auth_token
        }
        
        print(f"📤 Request: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")
            
            return result
        except Exception as e:
            print(f"❌ Multilingual test failed: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise
    
    async def test_trip_planning(self, session_id: int = SESSION_ID) -> Dict[str, Any]:
        """Test trip planning functionality."""
        print("\n" + "="*60)
        print("TEST 5: Trip Planning")
        print("="*60)
        
        payload = {
            "session_id": session_id,
            "message": "Plan a 3-day trip to Jeju Island with budget $1000",
            "auth_token": self.auth_token
        }
        
        print(f"📤 Request: {json.dumps(payload, indent=2)}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")
            
            return result
        except Exception as e:
            print(f"❌ Trip planning test failed: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise
    
    async def test_place_search(self, session_id: int = SESSION_ID) -> Dict[str, Any]:
        """Test place search functionality."""
        print("\n" + "="*60)
        print("TEST 6: Place Search - Specific Query")
        print("="*60)
        
        payload = {
            "session_id": session_id,
            "message": "Find N Seoul Tower information",
            "auth_token": self.auth_token
        }
        
        print(f"📤 Request: {json.dumps(payload, indent=2)}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")
            
            return result
        except Exception as e:
            print(f"❌ Place search test failed: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise
    
    async def test_error_handling_no_token(self, session_id: int = SESSION_ID):
        """Test error handling when token is missing."""
        print("\n" + "="*60)
        print("TEST 7: Error Handling - Missing Token")
        print("="*60)
        
        payload = {
            "session_id": session_id,
            "message": "Test message"
            # Missing auth_token intentionally
        }
        
        print(f"📤 Request: {json.dumps(payload, indent=2)}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            print(f"❌ Should have failed but got: {response.status_code}")
            print(f"Response: {response.text}")
        except httpx.HTTPStatusError as e:
            print(f"✅ Correctly rejected request: {e.response.status_code}")
            print(f"✅ Error message: {e.response.text[:200]}")
        except Exception as e:
            print(f"✅ Request failed as expected: {type(e).__name__}")
    
    async def test_streaming_chat(self, session_id: int = SESSION_ID):
        """Test streaming chat endpoint."""
        print("\n" + "="*60)
        print("TEST 8: Streaming Chat")
        print("="*60)
        
        payload = {
            "session_id": session_id,
            "message": "Tell me about Gyeongbokgung Palace",
            "auth_token": self.auth_token
        }
        
        print(f"📤 Request: {json.dumps(payload, indent=2)}")
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat/stream",
                json=payload
            ) as response:
                print(f"✅ Status: {response.status_code}")
                print("✅ Streaming events:")
                
                event_count = 0
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        event_count += 1
                        data = line[6:]  # Remove "data: " prefix
                        try:
                            event = json.loads(data)
                            print(f"  Event {event_count}: {event.get('type', 'unknown')}")
                            if event_count <= 3:  # Show first 3 events
                                print(f"    {json.dumps(event, indent=4, ensure_ascii=False)[:200]}")
                        except:
                            pass
                
                print(f"✅ Received {event_count} streaming events")
                
        except Exception as e:
            print(f"❌ Streaming test failed: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")


async def run_all_tests():
    """Run all tests sequentially."""
    print("\n" + "🚀"*30)
    print("AI TRAVEL AGENT - TEST SUITE")
    print("🚀"*30)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Auth Token: {AUTH_TOKEN[:20]}...")
    print(f"Session ID: {SESSION_ID}")
    
    tester = AgentTester()
    
    try:
        # Test 1: Health check
        await tester.test_health()
        
        # Test 2: Basic chat
        await tester.test_chat_basic()
        
        # Test 3: Chat with trip context
        await tester.test_chat_with_trip()
        
        # Test 4: Multilingual support
        await tester.test_multilingual()
        
        # Test 5: Trip planning
        await tester.test_trip_planning()
        
        # Test 6: Place search
        await tester.test_place_search()
        
        # Test 7: Error handling
        await tester.test_error_handling_no_token()
        
        # Test 8: Streaming chat
        await tester.test_streaming_chat()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST SUITE FAILED: {e}")
        print("="*60)
        raise
    finally:
        await tester.close()


async def run_single_test(test_name: str):
    """Run a single test by name."""
    tester = AgentTester()
    
    tests = {
        "health": tester.test_health,
        "basic": tester.test_chat_basic,
        "trip": tester.test_chat_with_trip,
        "multilingual": tester.test_multilingual,
        "planning": tester.test_trip_planning,
        "search": tester.test_place_search,
        "error": tester.test_error_handling_no_token,
        "stream": tester.test_streaming_chat,
    }
    
    if test_name in tests:
        try:
            await tests[test_name]()
        finally:
            await tester.close()
    else:
        print(f"❌ Unknown test: {test_name}")
        print(f"Available tests: {', '.join(tests.keys())}")


async def quick_test():
    """Quick test - just health and basic chat."""
    print("\n" + "⚡"*30)
    print("QUICK TEST")
    print("⚡"*30)
    
    tester = AgentTester()
    
    try:
        await tester.test_health()
        await tester.test_chat_basic()
        
        print("\n✅ Quick test completed!")
    finally:
        await tester.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            # Quick test
            asyncio.run(quick_test())
        else:
            # Run specific test
            asyncio.run(run_single_test(sys.argv[1]))
    else:
        # Run all tests
        asyncio.run(run_all_tests())
