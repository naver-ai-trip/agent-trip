"""Quick test for trip planning bug."""
import asyncio
import json
from src.utils.context import set_auth_token
from src.graph.state import AgentState
from src.graph.nodes import search_and_plan, generate_response


AUTH_TOKEN = "7|SXQRsdEG9gmd0PdtqHfwHegZYSYXqfEbRmPrMwFE63756727"


async def test_trip_planning_detection():
    """Test that trip planning is correctly detected."""
    print("\n" + "="*70)
    print("DEBUGGING TRIP PLANNING TYPE")
    print("="*70)
    
    set_auth_token(AUTH_TOKEN)
    
    initial_state: AgentState = {
        "messages": [],
        "auth_token": AUTH_TOKEN,
        "session_id": 3,
        "trip_id": 5,
        "user_message": "Plan me a 3 day trip in gangnam, from 23/11/2025 to 25/11/2025",
        "destination": None,
        "travel_dates": None,
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "en",
        "trigger_image_translation": False
    }
    
    print(f"\nUser message: {initial_state['user_message']}")
    print(f"Initial destination: {initial_state.get('destination')}")
    
    # Run search_and_plan
    print("\nRunning search_and_plan...")
    state_after_search = await search_and_plan(initial_state)
    
    print(f"\nAfter search_and_plan:")
    print(f"   - request_type: {state_after_search.get('request_type')}")
    print(f"   - num_days: {state_after_search.get('num_days')}")
    print(f"   - places_found: {len(state_after_search.get('places_found', []))}")
    print(f"   - destination: {state_after_search.get('destination')}")
    print(f"   - actions: {state_after_search.get('actions_taken')}")
    
    # Check if places have time info
    if state_after_search.get("places_found"):
        first_place = state_after_search["places_found"][0]
        print(f"\nFirst place sample:")
        print(f"   - name: [Place name]")
        print(f"   - day: {first_place.get('day')}")
        print(f"   - start_time: {first_place.get('start_time')}")
        print(f"   - end_time: {first_place.get('end_time')}")
        print(f"   - activity_type: {first_place.get('activity_type')}")
    
    # Run generate_response
    print("\nRunning generate_response...")
    state_after_response = await generate_response(state_after_search)
    
    response = state_after_response.get("final_response", {})
    components = response.get("components", [])
    
    print(f"\nAfter generate_response:")
    print(f"   - message: {response.get('message', '')[:80]}...")
    print(f"   - components count: {len(components)}")
    if components:
        print(f"   - first component type: {components[0].get('type')}")
    
    # Print full component structure
    if components:
        print(f"\nComponent structure:")
        print(json.dumps(components[0], indent=2, ensure_ascii=True)[:400] + "...")


if __name__ == "__main__":
    asyncio.run(test_trip_planning_detection())
