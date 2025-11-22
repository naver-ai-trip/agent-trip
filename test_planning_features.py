"""Test the improved planning features."""

import asyncio
import json
from src.utils.context import set_auth_token
from src.graph.agent import agent_graph
from src.graph.state import AgentState


AUTH_TOKEN = "7|SXQRsdEG9gmd0PdtqHfwHegZYSYXqfEbRmPrMwFE63756727"


async def test_suggest_places():
    """Test Suggest Places feature."""
    print("\n" + "="*70)
    print("TEST 1: SUGGEST PLACES FEATURE")
    print("="*70)
    
    set_auth_token(AUTH_TOKEN)
    
    initial_state: AgentState = {
        "messages": [],
        "auth_token": AUTH_TOKEN,
        "session_id": 3,
        "trip_id": None,
        "user_message": "Suggest me some places to visit in Seoul for 2 days",
        "destination": "Seoul",
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "en",
        "trigger_image_translation": False
    }
    
    try:
        result = await agent_graph.ainvoke(initial_state)
        
        response = result.get("final_response", {})
        print(f"\n✅ Message: {response.get('message', '')}")
        print(f"\n📍 Places found: {len(result.get('places_found', []))}")
        print(f"\n📋 Actions: {result.get('actions_taken', [])}")
        
        # Show sample places
        places = result.get("places_found", [])
        if places:
            print(f"\n🏛️ Sample places:")
            for i, place in enumerate(places[:3], 1):
                print(f"  {i}. {place.get('name')} ({place.get('category', 'N/A')})")
        
        # Print full response structure
        print(f"\n📄 Response Structure:")
        print(json.dumps(response, indent=2, ensure_ascii=False)[:500] + "...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_trip_planning():
    """Test Trip Planning feature."""
    print("\n" + "="*70)
    print("TEST 2: TRIP PLANNING FEATURE")
    print("="*70)
    
    set_auth_token(AUTH_TOKEN)
    
    initial_state: AgentState = {
        "messages": [],
        "auth_token": AUTH_TOKEN,
        "session_id": 3,
        "trip_id": 5,
        "user_message": "Plan me a 2 day trip in Seoul from 23/11/2025 to 24/11/2025",
        "destination": "Seoul",
        "travel_dates": {
            "start": "2025-11-23",
            "end": "2025-11-24"
        },
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "en",
        "trigger_image_translation": False
    }
    
    try:
        result = await agent_graph.ainvoke(initial_state)
        
        response = result.get("final_response", {})
        print(f"\n✅ Message: {response.get('message', '')}")
        print(f"\n📍 Total activities: {len(result.get('places_found', []))}")
        print(f"\n📋 Actions: {result.get('actions_taken', [])}")
        
        # Show itinerary by day
        components = response.get("components", [])
        if components:
            print(f"\n📅 ITINERARY:")
            for component in components:
                if component.get("type") == "itinerary_day":
                    data = component.get("data", {})
                    day = data.get("day")
                    date = data.get("date")
                    places = data.get("places", [])
                    
                    print(f"\n  Day {day} ({date}):")
                    for place in places:
                        start = place.get("start_time")
                        end = place.get("end_time")
                        name = place.get("name")
                        activity_type = place.get("activity_type", "")
                        meal_type = place.get("meal_type", "")
                        
                        if meal_type:
                            print(f"    {start}-{end}: 🍽️  {name} ({meal_type})")
                        else:
                            print(f"    {start}-{end}: 🏛️  {name}")
        
        # Print full response structure (partial)
        print(f"\n📄 Response Structure (first 800 chars):")
        print(json.dumps(response, indent=2, ensure_ascii=False)[:800] + "...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print("\n" + "🧪"*35)
    print("AI TRAVEL AGENT - IMPROVED PLANNING FEATURES TEST")
    print("🧪"*35)
    
    # Test 1: Suggest Places
    await test_suggest_places()
    
    print("\n" + "-"*70 + "\n")
    
    # Test 2: Trip Planning
    await test_trip_planning()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
