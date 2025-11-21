"""
Example Usage of the AI Travel Planning Agent

This file demonstrates how to interact with the agent programmatically.
"""

import asyncio
import json
from src.graph.agent import agent_graph
from src.graph.state import AgentState


async def example_simple_search():
    """Example: Simple place search in Seoul."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Place Search")
    print("="*60)
    
    state: AgentState = {
        "messages": [],
        "session_id": 2,
        "trip_id": 4,
        "user_message": "Show me popular restaurants in Seoul",
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "en",
        "trigger_image_translation": False
    }
    
    result = await agent_graph.ainvoke(state)
    
    print("\nResponse:")
    print(json.dumps(result.get("final_response"), indent=2, ensure_ascii=False))


async def example_multilingual_search():
    """Example: Search in Korean language."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multilingual Search (Korean)")
    print("="*60)
    
    state: AgentState = {
        "messages": [],
        "session_id": 2,
        "trip_id": 4,
        "user_message": "서울의 역사적인 궁궐을 보여주세요",  # Show me historical palaces in Seoul
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "ko",
        "trigger_image_translation": False
    }
    
    result = await agent_graph.ainvoke(state)
    
    print("\nResponse:")
    print(json.dumps(result.get("final_response"), indent=2, ensure_ascii=False))


async def example_image_translation():
    """Example: Image translation request."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Image Translation Request")
    print("="*60)
    
    state: AgentState = {
        "messages": [],
        "session_id": 2,
        "trip_id": 4,
        "user_message": "Please translate this image for me",
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "en",
        "trigger_image_translation": False
    }
    
    result = await agent_graph.ainvoke(state)
    
    print("\nResponse:")
    print(json.dumps(result.get("final_response"), indent=2, ensure_ascii=False))


async def example_with_full_context():
    """Example: Search with full session context."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Search with Full Session Context")
    print("="*60)
    
    state: AgentState = {
        "messages": [],
        "session_id": 2,
        "trip_id": 4,
        "user_id": 3,
        "destination": "Seoul, South Korea",
        "budget": "moderate",
        "interests": ["food", "culture", "history"],
        "travel_dates": {
            "start": "2025-12-01",
            "end": "2025-12-07"
        },
        "user_message": "Recommend places based on my interests",
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "en",
        "trigger_image_translation": False
    }
    
    result = await agent_graph.ainvoke(state)
    
    print("\nResponse:")
    print(json.dumps(result.get("final_response"), indent=2, ensure_ascii=False))
    
    print("\nPlaces found:", len(result.get("places_found", [])))
    print("Actions taken:", result.get("actions_taken"))


async def example_api_usage():
    """Example: Using the API client directly."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Direct API Client Usage")
    print("="*60)
    
    from src.utils.api_client import api_client
    from src.tools.place_tools import search_places_by_text
    
    # Search for places
    print("\nSearching for 'Seoul restaurants'...")
    places = await search_places_by_text.ainvoke({"query": "Seoul restaurants"})
    
    print(f"\nFound {len(places)} places:")
    for i, place in enumerate(places[:3], 1):  # Show first 3
        print(f"\n{i}. {place.get('name')}")
        print(f"   Category: {place.get('category')}")
        print(f"   Address: {place.get('address')}")
        print(f"   Rating: {place.get('rating')}")
    
    # Close client
    await api_client.close()


async def example_streaming():
    """Example: Streaming response."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Streaming Execution")
    print("="*60)
    
    state: AgentState = {
        "messages": [],
        "session_id": 2,
        "trip_id": 4,
        "user_message": "Find tourist attractions in Seoul",
        "places_found": [],
        "actions_taken": [],
        "next_suggestions": [],
        "iteration_count": 0,
        "user_language": "en",
        "trigger_image_translation": False
    }
    
    print("\nStreaming execution progress:")
    async for event in agent_graph.astream(state):
        for node_name, node_state in event.items():
            print(f"  → {node_name}")
            if node_state.get("actions_taken"):
                for action in node_state["actions_taken"]:
                    print(f"    • {action}")
    
    print("\n✓ Execution complete")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("AI TRAVEL PLANNING AGENT - EXAMPLES")
    print("="*60)
    
    print("\nThese examples demonstrate the agent's capabilities.")
    print("Make sure the .env file is configured with valid credentials.\n")
    
    try:
        # Run examples
        await example_simple_search()
        await asyncio.sleep(1)
        
        await example_multilingual_search()
        await asyncio.sleep(1)
        
        await example_image_translation()
        await asyncio.sleep(1)
        
        await example_with_full_context()
        await asyncio.sleep(1)
        
        await example_api_usage()
        await asyncio.sleep(1)
        
        await example_streaming()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nMake sure:")
        print("1. .env file is configured")
        print("2. Backend API is accessible")
        print("3. All dependencies are installed")


if __name__ == "__main__":
    asyncio.run(main())
