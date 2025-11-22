"""State definition for the LangGraph agent."""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage


class AgentState(MessagesState):
    """State for the travel planning agent.
    
    Extends MessagesState to include conversation history and adds
    custom fields for travel planning context.
    """
    
    # Authentication
    auth_token: Optional[str] = None  # Bearer token for backend API
    
    # Chat session context
    session_id: Optional[int] = None
    trip_id: Optional[int] = None
    user_id: Optional[int] = None
    
    # Session context from backend
    destination: Optional[str] = None
    budget: Optional[str] = None
    interests: List[str] = []
    travel_dates: Optional[Dict[str, str]] = None
    
    # User's detected language
    user_language: str = "en"
    
    # Current user message (latest only - for intent extraction)
    user_message: str = ""
    
    # Intent detected from latest message
    intent_type: Optional[str] = None  # conversation, trip_planning, suggest_places, rag_query
    
    # Search and planning results
    places_found: List[Dict[str, Any]] = []
    request_type: Optional[str] = None  # "trip_planning" or "suggest_places"
    num_days: int = 1  # Number of days for trip planning
    
    # RAG (Knowledge retrieval) results
    rag_documents: List[Dict[str, Any]] = []
    rag_answer: Optional[str] = None
    rag_cited_sources: List[Dict[str, Any]] = []
    
    # Final response to send
    final_response: Optional[Dict[str, Any]] = None
    
    # Actions taken during processing
    actions_taken: List[str] = []
    
    # Next suggested actions for user
    next_suggestions: List[str] = []
    
    # Whether to trigger image translation in UI
    trigger_image_translation: bool = False
    
    # Iteration control
    iteration_count: int = 0
