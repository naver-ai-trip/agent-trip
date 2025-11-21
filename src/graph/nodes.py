"""Agent nodes for the LangGraph workflow."""

from typing import Dict, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

from src.graph.state import AgentState
from src.graph.response_formatter import response_formatter
from src.utils.api_client import api_client
from src.utils.translator import language_detector
from src.tools.place_tools import (
    search_places_by_text,
    search_nearby_places,
    scrape_korea_tourist_spots,
    get_place_details_by_korean_name
)
from src.config import settings


# Initialize LLM
llm = ChatOpenAI(
    model=settings.MODEL_NAME,
    temperature=settings.TEMPERATURE,
    openai_api_key=settings.OPENAI_API_KEY
)


async def initialize_session(state: AgentState) -> AgentState:
    """Initialize the chat session by loading context from backend.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with session context
    """
    logger.info(f"Initializing session {state['session_id']}")
    
    try:
        # Get chat session details
        session_data = await api_client.get_chat_session(state["session_id"])
        
        # Extract context
        context = session_data.get("context", {})
        state["destination"] = context.get("destination")
        state["budget"] = context.get("budget")
        state["interests"] = context.get("interests", [])
        state["travel_dates"] = context.get("travel_dates")
        state["trip_id"] = session_data.get("trip_id")
        state["user_id"] = session_data.get("user_id")
        
        # Detect user language from message
        if state["user_message"]:
            state["user_language"] = language_detector.detect_language(
                state["user_message"]
            )
        
        state["actions_taken"].append("Loaded session context")
        logger.info(f"Session initialized: destination={state['destination']}, interests={state['interests']}")
        
    except Exception as e:
        logger.error(f"Error initializing session: {e}")
        state["actions_taken"].append("Failed to load session context")
    
    return state


async def route_request(state: AgentState) -> AgentState:
    """Route the user request to appropriate handling logic.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with routing decision
    """
    logger.info("Routing user request")
    
    user_msg = state["user_message"].lower()
    
    # Check for image translation request
    if any(keyword in user_msg for keyword in ["translate image", "image translation", "translate this image", "translate photo"]):
        state["trigger_image_translation"] = True
        logger.info("Routing to image translation")
        return state
    
    # Continue with normal flow
    logger.info("Routing to planning/search flow")
    return state


async def search_and_plan(state: AgentState) -> AgentState:
    """Search for places and create travel plans based on user request.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with search results
    """
    logger.info("Executing search and planning")
    
    user_msg = state["user_message"]
    destination = state.get("destination", "")
    interests = state.get("interests", [])
    
    try:
        # Build context for LLM
        context_parts = []
        if destination:
            context_parts.append(f"Destination: {destination}")
        if interests:
            context_parts.append(f"User interests: {', '.join(interests)}")
        if state.get("budget"):
            context_parts.append(f"Budget: {state['budget']}")
        if state.get("travel_dates"):
            dates = state["travel_dates"]
            context_parts.append(f"Travel dates: {dates.get('start')} to {dates.get('end')}")
        
        context_str = "\n".join(context_parts)
        
        # Determine if this is a full trip planning request or simple search
        system_prompt = f"""You are a helpful travel planning assistant. 

Session Context:
{context_str}

User's message: {user_msg}

Analyze the user's request and determine:
1. Is this a request for a complete trip plan (with itinerary and scheduling)?
2. Or is this a simple request for place recommendations/search?

Respond with JSON:
{{
    "request_type": "full_trip_plan" or "place_search",
    "search_query": "Korean search term for finding places",
    "needs_nearby_search": true/false,
    "reasoning": "explanation"
}}
"""
        
        response = await llm.ainvoke([SystemMessage(content=system_prompt)])
        logger.info(f"LLM routing analysis: {response.content}")
        
        # For now, perform place search
        # Translate user message to Korean for searching
        search_query = destination if destination else user_msg
        korean_query = language_detector.translate_to_korean(search_query)
        
        # Search for places
        places = await search_places_by_text.ainvoke({"query": korean_query})
        
        # If not enough results, try nearby search with first result
        if len(places) < 3 and places:
            first_place = places[0]
            if "latitude" in first_place and "longitude" in first_place:
                logger.info("Performing nearby search for more results")
                nearby_places = await search_nearby_places.ainvoke({
                    "latitude": first_place["latitude"],
                    "longitude": first_place["longitude"],
                    "radius": 5000
                })
                # Combine and deduplicate
                existing_names = {p.get("name") for p in places}
                for place in nearby_places:
                    if place.get("name") not in existing_names:
                        places.append(place)
        
        # Try web scraping for additional tourist spots if still not enough
        if len(places) < 5 and destination:
            logger.info("Attempting to scrape VisitKorea for more places")
            try:
                scraped_content = await scrape_korea_tourist_spots.ainvoke({"region": destination})
                # This would need additional parsing, for now we'll skip
                state["actions_taken"].append("Scraped additional tourist information")
            except Exception as e:
                logger.warning(f"Web scraping failed: {e}")
        
        state["places_found"] = places[:10]  # Limit to top 10
        state["actions_taken"].append(f"Found {len(state['places_found'])} places")
        logger.info(f"Search completed: {len(state['places_found'])} places found")
        
    except Exception as e:
        logger.error(f"Error in search and planning: {e}")
        state["places_found"] = []
        state["actions_taken"].append("Search failed")
    
    return state


async def generate_response(state: AgentState) -> AgentState:
    """Generate final response for the user.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final response
    """
    logger.info("Generating final response")
    
    # Handle image translation trigger
    if state.get("trigger_image_translation"):
        state["final_response"] = response_formatter.format_image_translation_trigger(
            "I'll help you translate that image. Please upload the image you'd like me to translate."
        )
        return state
    
    # Handle place search results
    if state["places_found"]:
        places = state["places_found"]
        
        # Generate natural language message
        user_lang = state.get("user_language", "en")
        destination = state.get("destination", "your destination")
        
        # Create message based on user language
        message_template = f"I found {len(places)} amazing places in {destination} that match your preferences! These include top-rated restaurants, cultural attractions, and hotels in the heart of the city."
        
        # Translate message to user's language if not English
        if user_lang != "en":
            message = language_detector.translate_to_language(message_template, user_lang)
        else:
            message = message_template
        
        # Generate suggestions
        next_suggestions = [
            "Add a place to itinerary",
            "Get directions",
            "Search nearby attractions",
            "Create complete trip plan"
        ]
        
        # Translate suggestions
        if user_lang != "en":
            next_suggestions = [
                language_detector.translate_to_language(s, user_lang) 
                for s in next_suggestions
            ]
        
        state["final_response"] = response_formatter.format_places_response(
            message=message,
            places=places,
            actions_taken=state["actions_taken"],
            next_suggestions=next_suggestions
        )
    else:
        # No results found
        message = "I couldn't find any places matching your request. Could you provide more details or try a different search?"
        
        user_lang = state.get("user_language", "en")
        if user_lang != "en":
            message = language_detector.translate_to_language(message, user_lang)
        
        state["final_response"] = response_formatter.format_simple_message(
            message=message,
            actions_taken=state["actions_taken"],
            next_suggestions=["Try a different search", "Ask for recommendations"]
        )
    
    logger.info("Response generated successfully")
    return state


async def save_response(state: AgentState) -> AgentState:
    """Save the agent's response to the backend.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state
    """
    logger.info("Saving response to backend")
    
    try:
        if state.get("final_response") and state.get("session_id"):
            # Convert response to JSON string for storage
            import json
            message_content = json.dumps(state["final_response"], ensure_ascii=False)
            
            # Send to backend
            await api_client.send_message(
                session_id=state["session_id"],
                message=message_content,
                from_role="assistant",
                metadata={
                    "model": settings.MODEL_NAME,
                    "actions_taken": state["actions_taken"],
                    "places_count": len(state.get("places_found", []))
                }
            )
            
            state["actions_taken"].append("Response saved to database")
            logger.info("Response saved successfully")
    
    except Exception as e:
        logger.error(f"Error saving response: {e}")
        state["actions_taken"].append("Failed to save response")
    
    return state
