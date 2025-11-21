"""Test utilities and helpers for the AI Travel Agent."""

import asyncio
from typing import Dict, Any
import json
from src.graph.agent import agent_graph
from src.graph.state import AgentState


class AgentTester:
    """Helper class for testing the agent."""
    
    @staticmethod
    async def test_message(
        session_id: int,
        message: str,
        trip_id: int = None,
        destination: str = None,
        interests: list = None
    ) -> Dict[str, Any]:
        """Test the agent with a message.
        
        Args:
            session_id: Chat session ID
            message: User message
            trip_id: Optional trip ID
            destination: Optional destination
            interests: Optional user interests
            
        Returns:
            Agent response
        """
        state: AgentState = {
            "messages": [],
            "session_id": session_id,
            "trip_id": trip_id,
            "user_message": message,
            "destination": destination,
            "interests": interests or [],
            "places_found": [],
            "actions_taken": [],
            "next_suggestions": [],
            "iteration_count": 0,
            "user_language": "en",
            "trigger_image_translation": False
        }
        
        result = await agent_graph.ainvoke(state)
        return result
    
    @staticmethod
    def print_response(result: Dict[str, Any]):
        """Pretty print agent response.
        
        Args:
            result: Agent result dictionary
        """
        print("\n" + "="*60)
        print("AGENT RESPONSE")
        print("="*60)
        
        final_response = result.get("final_response", {})
        
        print("\nMessage:")
        print(final_response.get("message", "No message"))
        
        print("\nComponents:")
        for component in final_response.get("components", []):
            print(f"  - Type: {component.get('type')}")
            if component.get("type") == "places_list":
                places = component.get("data", {}).get("places", [])
                print(f"    Places count: {len(places)}")
        
        print("\nActions Taken:")
        for action in final_response.get("actions_taken", []):
            print(f"  • {action}")
        
        print("\nNext Suggestions:")
        for suggestion in final_response.get("next_suggestions", []):
            print(f"  → {suggestion}")
        
        print("\n" + "="*60)


async def quick_test():
    """Quick test of the agent."""
    print("Running quick test...")
    
    tester = AgentTester()
    
    # Test 1: Simple search
    print("\n\nTest 1: Simple place search")
    result = await tester.test_message(
        session_id=2,
        message="Show me restaurants in Seoul",
        trip_id=4,
        destination="Seoul"
    )
    tester.print_response(result)
    
    # Test 2: Image translation
    print("\n\nTest 2: Image translation request")
    result = await tester.test_message(
        session_id=2,
        message="Translate this image",
        trip_id=4
    )
    tester.print_response(result)


if __name__ == "__main__":
    asyncio.run(quick_test())
