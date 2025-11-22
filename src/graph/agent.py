"""Main LangGraph workflow definition."""

import logging
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

from src.graph.state import AgentState
from src.graph.nodes import (
    initialize_session,
    route_request,
    casual_conversation,
    search_and_plan,
    handle_rag_query,
    generate_response,
    save_response
)


def create_agent_graph():
    """Create and compile the LangGraph agent workflow.
    
    Flow:
    1. Initialize session (load context)
    2. Route request (detect intent from latest message)
    3. Branch based on intent:
       - conversation: casual chat with suggestions
       - trip_planning: create itinerary
       - suggest_places: find destinations
       - rag_query: culture/history/tips
    4. Generate response
    5. Save to backend
    
    Returns:
        Compiled graph ready for execution
    """
    logger.info("Creating agent graph")
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_session)
    workflow.add_node("route", route_request)
    workflow.add_node("conversation", casual_conversation)
    workflow.add_node("search_plan", search_and_plan)
    workflow.add_node("rag_query", handle_rag_query)
    workflow.add_node("generate", generate_response)
    workflow.add_node("save", save_response)
    
    # Define edges
    workflow.set_entry_point("initialize")
    
    workflow.add_edge("initialize", "route")
    
    # Conditional routing based on intent detected from latest message
    def should_route(state: AgentState) -> str:
        """Determine routing based on intent_type."""
        intent = state.get("intent_type")
        
        # Image translation takes priority
        if state.get("trigger_image_translation"):
            return "generate"
        
        # Route based on detected intent
        if intent == "rag_query":
            return "rag_query"
        elif intent == "trip_planning" or intent == "suggest_places":
            return "search_plan"
        elif intent == "conversation":
            return "conversation"
        
        # Default: conversation
        return "conversation"
    
    workflow.add_conditional_edges(
        "route",
        should_route,
        {
            "conversation": "conversation",
            "search_plan": "search_plan",
            "rag_query": "rag_query",
            "generate": "generate"
        }
    )
    
    workflow.add_edge("conversation", "generate")
    workflow.add_edge("search_plan", "generate")
    workflow.add_edge("rag_query", "generate")
    workflow.add_edge("generate", "save")
    workflow.add_edge("save", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("Agent graph compiled successfully")
    return app


# Create the global agent instance
agent_graph = create_agent_graph()
