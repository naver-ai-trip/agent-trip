"""Main LangGraph workflow definition."""

import logging
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

from src.graph.state import AgentState
from src.graph.nodes import (
    initialize_session,
    route_request,
    search_and_plan,
    generate_response,
    save_response
)


def create_agent_graph():
    """Create and compile the LangGraph agent workflow.
    
    Returns:
        Compiled graph ready for execution
    """
    logger.info("Creating agent graph")
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_session)
    workflow.add_node("route", route_request)
    workflow.add_node("search_plan", search_and_plan)
    workflow.add_node("generate", generate_response)
    workflow.add_node("save", save_response)
    
    # Define edges
    workflow.set_entry_point("initialize")
    
    workflow.add_edge("initialize", "route")
    
    # Conditional routing based on request type
    def should_search(state: AgentState) -> str:
        """Determine if we should perform search or go straight to response."""
        if state.get("trigger_image_translation"):
            return "generate"
        return "search_plan"
    
    workflow.add_conditional_edges(
        "route",
        should_search,
        {
            "search_plan": "search_plan",
            "generate": "generate"
        }
    )
    
    workflow.add_edge("search_plan", "generate")
    workflow.add_edge("generate", "save")
    workflow.add_edge("save", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("Agent graph compiled successfully")
    return app


# Create the global agent instance
agent_graph = create_agent_graph()
