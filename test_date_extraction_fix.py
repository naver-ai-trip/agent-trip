"""Test date extraction with agent flow."""
import asyncio
from src.utils.context import set_auth_token
from src.graph.state import AgentState
from src.graph.nodes import search_and_plan

AUTH_TOKEN = "7|SXQRsdEG9gmd0PdtqHfwHegZYSYXqfEbRmPrMwFE63756727"

async def test_date_extraction():
    """Test that date range is prioritized over text."""
    
    set_auth_token(AUTH_TOKEN)
    
    # Test case: message says "3 day" but dates are 22 to 25 (4 days)
    state: AgentState = {
        "messages": [],
        "auth_token": AUTH_TOKEN,
        "session_id": 3,
        "trip_id": 5,
        "user_message": "Plan me 3 day trip to Korea from 22/11/2025 to 25/11/2025",
        "destination": None,
        "travel_dates": None,
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "en",
        "trigger_image_translation": False
    }
    
    print("="*70)
    print("DATE EXTRACTION TEST")
    print("="*70)
    print(f"Message: {state['user_message']}")
    print(f"Expected: 4 days (22, 23, 24, 25 Nov)")
    
    result = await search_and_plan(state)
    
    print(f"\nResult:")
    print(f"  num_days: {result.get('num_days')}")
    print(f"  request_type: {result.get('request_type')}")
    print(f"  places_found: {len(result.get('places_found', []))}")
    
    # Check day distribution
    days = {}
    for place in result.get('places_found', []):
        day = place.get('day')
        if day:
            if day not in days:
                days[day] = []
            days[day].append(place.get('name', 'Unknown'))
    
    print(f"  days scheduled: {sorted(days.keys())}")
    for day in sorted(days.keys()):
        print(f"    Day {day}: {len(days[day])} activities")
    
    print(f"\n{'PASS' if result.get('num_days') == 4 else 'FAIL'}: Expected 4 days, got {result.get('num_days')}")
    print(f"{'PASS' if len(days) == 4 else 'PARTIAL'}: Scheduled {len(days)} out of 4 days")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_date_extraction())
