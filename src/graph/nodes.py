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
from src.utils.context import set_auth_token
from src.tools.place_tools import (
    search_places_by_text,
    search_nearby_places,
    scrape_korea_tourist_spots,
    get_place_details_by_korean_name
)
from src.tools.rag_tools import (
    is_rag_query,
    embed_query,
    search_vector_db,
    rerank_documents,
    fetch_document_metadata
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
    
    # Set auth token in context for tools to use
    if state.get("auth_token"):
        set_auth_token(state["auth_token"])
    
    try:
        # Get chat session details
        auth_token = state.get("auth_token")
        session_data = await api_client.get_chat_session(state["session_id"], auth_token)
        
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
    
    Analyzes the LATEST user message to determine intent:
    - Casual conversation (greetings, general chat)
    - Trip planning (create itinerary)
    - Place suggestions (find destinations)
    - RAG query (culture, history, tips)
    
    Note: Conversation history provides context, but intent is extracted from latest message only.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with routing decision
    """
    logger.info("Routing user request - analyzing latest message intent")
    
    user_msg = state["user_message"]
    user_msg_lower = user_msg.lower()
    
    # Check for image translation request
    if any(keyword in user_msg_lower for keyword in ["translate image", "image translation", "translate this image", "translate photo"]):
        state["trigger_image_translation"] = True
        state["intent_type"] = "image_translation"
        logger.info("Intent: Image Translation")
        return state
    
    # 1. Check for RAG queries (culture, history, customs, tips)
    # RAG keywords: culture, history, custom, etiquette, tradition, tip, insight, about, dynasty, palace, temple
    if settings.RAG_ENABLED and is_rag_query(user_msg):
        state["intent_type"] = "rag_query"
        state["actions_taken"].append("rag_query_detected")
        logger.info("Intent: RAG Query (culture/history/tips)")
        return state
    
    # 2. Check for trip planning keywords (create itinerary, plan trip)
    trip_planning_keywords = [
        "plan", "itinerary", "schedule", "trip plan", "travel plan",
        "계획", "일정", "여행 계획", "스케줄"
    ]
    if any(keyword in user_msg_lower for keyword in trip_planning_keywords):
        state["intent_type"] = "trip_planning"
        logger.info("Intent: Trip Planning")
        return state
    
    # 3. Check for place suggestion keywords (find, recommend, suggest)
    place_keywords = [
        "suggest", "recommend", "find", "show me", "looking for", "search",
        "추천", "찾아", "보여", "검색"
    ]
    if any(keyword in user_msg_lower for keyword in place_keywords):
        state["intent_type"] = "suggest_places"
        logger.info("Intent: Suggest Places")
        return state
    
    # 4. Default to casual conversation (greetings, general chat)
    # This handles: hi, hello, how are you, tell me about yourself, etc.
    state["intent_type"] = "conversation"
    logger.info("Intent: Casual Conversation")
    return state


async def casual_conversation(state: AgentState) -> AgentState:
    """Handle casual conversation with suggestions for next actions.
    
    When user says hi or engages in general conversation, respond warmly
    and suggest options: plan trip, find destinations, or learn about culture.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with conversational response
    """
    logger.info("Handling casual conversation")
    
    user_msg = state["user_message"]
    destination = state.get("destination", "Korea")
    
    try:
        # Use LLM to generate friendly conversational response
        system_prompt = f"""You are Traver - a Naver AI-powered travel planning platform. You assist with research, planning, risk detection, booking, and coordination in one unified system.

Respond warmly and naturally to their message, then suggest helpful options:
1. Plan a trip (create an itinerary with research and coordination)
2. Find destinations (discover places to visit with AI-powered recommendations)
3. Learn about Korean culture (history, customs, etiquette from your knowledge base)

Keep the response concise (2-3 sentences) and friendly. Emphasize your AI-powered capabilities.
Destination context: {destination}

User message: {user_msg}"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_msg)
        ]
        
        response = await llm.ainvoke(messages)
        conversational_response = response.content.strip()
        
        # Set response
        state["rag_answer"] = conversational_response  # Reuse rag_answer for text response
        state["actions_taken"].append("casual_conversation")
        
        # Suggest next actions
        state["next_suggestions"] = [
            "Plan my trip",
            "Find places to visit",
            "Learn about Korean culture"
        ]
        
        logger.info("Casual conversation response generated")
        
    except Exception as e:
        logger.error(f"Error in casual conversation: {e}", exc_info=True)
        state["rag_answer"] = (
            f"Hello! I'm Traver, your Naver AI-powered travel planning platform. "
            f"I handle research, planning, risk detection, booking, and coordination in one unified system.\n\n"
            f"How can I assist you today?\n"
            f"• Plan an intelligent trip to {destination}\n"
            f"• Discover AI-recommended places to visit\n"
            f"• Learn about Korean culture and customs from my knowledge base"
        )
        state["next_suggestions"] = ["Plan my trip", "Find places", "Learn about culture"]
    
    return state


async def search_and_plan(state: AgentState) -> AgentState:
    """Search for places and create travel plans based on user request.
    Supports two modes: Suggest Places and Trip Planning.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with search results and planning data
    """
    logger.info("Executing search and planning")
    
    user_msg = state["user_message"].lower()
    destination = state.get("destination", "")
    interests = state.get("interests", [])
    travel_dates = state.get("travel_dates")
    
    # Detect request type based on keywords
    is_trip_planning = any(keyword in user_msg for keyword in ["plan", "itinerary", "schedule", "trip plan"])
    is_suggest = any(keyword in user_msg for keyword in ["suggest", "recommend", "find", "show me"])
    
    try:
        # Calculate number of days
        num_days = 1
        
        # First check travel_dates from session context
        if travel_dates and travel_dates.get("start") and travel_dates.get("end"):
            from datetime import datetime
            try:
                start = datetime.fromisoformat(str(travel_dates["start"]).replace('/', '-'))
                end = datetime.fromisoformat(str(travel_dates["end"]).replace('/', '-'))
                num_days = (end - start).days + 1
                logger.info(f"Extracted {num_days} days from session travel_dates")
            except:
                pass
        
        # Try to extract from user message if not in context
        if num_days == 1:
            import re
            
            # PRIORITY 1: Try to find date ranges first (more accurate than text)
            date_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
            dates = re.findall(date_pattern, user_msg)
            if len(dates) >= 2:
                try:
                    from datetime import datetime
                    # Parse first date (start)
                    start = datetime(int(dates[0][2]), int(dates[0][1]), int(dates[0][0]))
                    # Parse second date (end)
                    end = datetime(int(dates[1][2]), int(dates[1][1]), int(dates[1][0]))
                    num_days = (end - start).days + 1
                    logger.info(f"Extracted {num_days} days from date range in message")
                except Exception as e:
                    logger.warning(f"Failed to parse date range: {e}")
            
            # PRIORITY 2: If no date range found, look for day count patterns
            if num_days == 1:
                # Look for patterns like "3 day trip", "5 days", "3-day", etc.
                day_match = re.search(r'(\d+)\s*[-\s]?\s*days?', user_msg)
                if day_match:
                    num_days = int(day_match.group(1))
                    logger.info(f"Extracted {num_days} days from text pattern")
        
        logger.info(f"Request type: {'Trip Planning' if is_trip_planning else 'Suggest Places'}, Days: {num_days}")
        
        # Extract destination from message if not in context
        if not destination:
            destination = await _extract_destination(user_msg)
        
        if is_trip_planning:
            # TRIP PLANNING MODE
            places = await _search_places_for_trip_planning(destination, interests, num_days)
            state["places_found"] = places
            state["request_type"] = "trip_planning"
            state["num_days"] = num_days
            state["actions_taken"].append(f"Created {num_days}-day trip plan with {len(places)} places")
            logger.info(f"Trip planning mode: {len(places)} places scheduled")
        else:
            # SUGGEST PLACES MODE
            places = await _search_places_for_suggestions(destination, interests, num_days)
            state["places_found"] = places[:10]  # Limit to 10 places
            state["request_type"] = "suggest_places"
            state["num_days"] = num_days
            state["actions_taken"].append(f"Found {len(state['places_found'])} suggested places")
            logger.info(f"Suggest mode: {len(state['places_found'])} places found")
        
        logger.info(f"Search completed: {len(state['places_found'])} places found, request_type: {state.get('request_type')}")
        
    except Exception as e:
        logger.error(f"Error in search and planning: {e}", exc_info=True)
        # Preserve places if they were found before error
        if not state.get("places_found"):
            state["places_found"] = []
        # Keep request_type if it was already set, otherwise default to suggest
        if not state.get("request_type"):
            state["request_type"] = "suggest_places"
        state["actions_taken"].append(f"Search completed with errors: {str(e)[:50]}")
    
    return state


async def _extract_destination(user_msg: str) -> str:
    """Extract destination from user message."""
    # Common Korean destinations
    destinations = ["seoul", "busan", "jeju", "incheon", "daegu", "gwangju", "daejeon",
                    "서울", "부산", "제주", "인천", "대구", "광주", "대전"]
    
    for dest in destinations:
        if dest in user_msg.lower():
            return dest.capitalize() if dest.isalpha() else dest
    
    return "Seoul"  # Default


async def _search_places_for_suggestions(destination: str, interests: list, num_days: int) -> list:
    """Search places for suggestion mode.
    
    Strategy:
    1. Scrape VisitKorea for tourist spots
    2. Get details for each Korean name
    3. Search places by text
    4. Search nearby places (multiple rounds if needed)
    5. Filter and return enough for all days (3-5 places + 2 restaurants per day)
    """
    # Calculate target: need enough places for all days
    target_attractions = num_days * 4  # 4 attractions per day minimum
    target_restaurants = num_days * 2  # 2 meals per day
    
    logger.info(f"Searching places for {num_days} days: target {target_attractions} attractions + {target_restaurants} restaurants")
    
    all_places = []
    restaurants = []
    
    # Step 1 & 2: Scrape VisitKorea and get details
    try:
        scraped_spots = await scrape_korea_tourist_spots.ainvoke({"region": destination})
        logger.info(f"Scraped {len(scraped_spots)} spots from VisitKorea")
        
        # Scale scraping based on trip length
        # Algorithm: base 10 + (5 per additional day) for longer trips
        # 1 day = 10, 2 days = 15, 3 days = 20, 4 days = 25, etc.
        # Cap at 30 to avoid excessive API calls
        base_scrape = 10
        per_day_scrape = 5
        max_scrape_limit = 30
        
        scrape_limit = min(
            max_scrape_limit,
            base_scrape + (per_day_scrape * (num_days - 1))
        )
        
        logger.info(f"Scraping up to {scrape_limit} places for {num_days}-day trip")
        
        # Get details for Korean names
        for spot in scraped_spots[:scrape_limit]:
            if spot.get("korean_name"):
                details = await get_place_details_by_korean_name.ainvoke({"korean_name": spot["korean_name"]})
                if details and details.get("name"):
                    all_places.append(details)
    except Exception as e:
        logger.warning(f"Error scraping VisitKorea: {e}")
    
    # Step 3: Search places by text
    try:
        search_query = destination
        if interests:
            search_query = f"{destination} {' '.join(interests[:2])}"
        
        text_results = await search_places_by_text.ainvoke({"query": search_query})
        logger.info(f"Found {len(text_results)} places from text search")
        
        # Separate restaurants and attractions
        for place in text_results:
            category = place.get("category", "").lower()
            if any(word in category for word in ["음식", "식당", "restaurant", "cafe", "카페"]):
                restaurants.append(place)
            else:
                all_places.append(place)
    except Exception as e:
        logger.warning(f"Error in text search: {e}")
    
    # Step 4: Search nearby places - do multiple rounds if needed
    nearby_search_count = 0
    max_nearby_searches = 3  # Limit to avoid too many API calls
    
    while len(all_places) < target_attractions and nearby_search_count < max_nearby_searches:
        if not all_places:
            break
            
        try:
            # Use different places as center points for variety
            center_place = all_places[min(nearby_search_count, len(all_places) - 1)]
            
            if center_place.get("latitude") and center_place.get("longitude"):
                # Increase radius for subsequent searches
                radius = 3000 + (nearby_search_count * 2000)
                nearby = await search_nearby_places.ainvoke({
                    "latitude": center_place["latitude"],
                    "longitude": center_place["longitude"],
                    "radius": radius
                })
                logger.info(f"Round {nearby_search_count + 1}: Found {len(nearby)} nearby places (radius {radius}m)")
                
                for place in nearby:
                    category = place.get("category", "").lower()
                    if any(word in category for word in ["음식", "식당", "restaurant", "cafe", "카페"]):
                        restaurants.append(place)
                    else:
                        all_places.append(place)
                
                nearby_search_count += 1
        except Exception as e:
            logger.warning(f"Error in nearby search round {nearby_search_count + 1}: {e}")
            break
    
    # Deduplicate by name
    seen_names = set()
    unique_places = []
    for place in all_places:
        if place.get("name") not in seen_names:
            seen_names.add(place.get("name"))
            unique_places.append(place)
    
    seen_restaurant_names = set()
    unique_restaurants = []
    for place in restaurants:
        if place.get("name") not in seen_restaurant_names:
            seen_restaurant_names.add(place.get("name"))
            unique_restaurants.append(place)
    
    # Combine: return enough places for all days
    # For suggest mode: limit to 10
    # For trip planning: return all (will be used by _search_places_for_trip_planning)
    max_attractions = max(10, num_days * 4)  # At least 10, or 4 per day
    max_restaurants = max(5, num_days * 2)   # At least 5, or 2 per day
    combined = unique_places[:max_attractions] + unique_restaurants[:max_restaurants]
    
    logger.info(f"Final suggestions: {len(unique_places[:max_attractions])} places, {len(unique_restaurants[:max_restaurants])} restaurants")
    return combined


async def _search_places_for_trip_planning(destination: str, interests: list, num_days: int) -> list:
    """Search places for trip planning mode with time scheduling.
    
    Returns places with start_time and end_time for each day.
    Each day: 8 AM - 9 PM, at least 3 places + lunch + dinner
    """
    logger.info(f"Planning trip for {destination}, {num_days} days")
    
    # Calculate minimum requirements
    min_attractions_per_day = 4
    min_restaurants_per_day = 2
    min_total_attractions = num_days * min_attractions_per_day
    min_total_restaurants = num_days * min_restaurants_per_day
    
    # Search all places first (reuse suggestion logic)
    all_results = await _search_places_for_suggestions(destination, interests, num_days)
    
    # Separate restaurants and attractions
    attractions = []
    restaurants = []
    
    for place in all_results:
        category = place.get("category", "").lower()
        if any(word in category for word in ["음식", "식당", "restaurant", "cafe", "카페"]):
            restaurants.append(place)
        else:
            attractions.append(place)
    
    logger.info(f"Found {len(attractions)} attractions and {len(restaurants)} restaurants")
    
    # Validate we have enough places
    if len(attractions) < min_total_attractions:
        logger.warning(f"Insufficient attractions: have {len(attractions)}, need {min_total_attractions}")
        # Adjust expectations: ensure at least 2 per day
        min_attractions_per_day = max(2, len(attractions) // num_days)
    
    if len(restaurants) < min_total_restaurants:
        logger.warning(f"Insufficient restaurants: have {len(restaurants)}, need {min_total_restaurants}")
        # Duplicate restaurants if needed for multiple days (people can visit same restaurant)
        if restaurants and len(restaurants) > 0:
            original_restaurants = restaurants.copy()
            while len(restaurants) < min_total_restaurants:
                # Add copies of existing restaurants
                for restaurant in original_restaurants:
                    if len(restaurants) >= min_total_restaurants:
                        break
                    # Create a copy with same data
                    restaurant_copy = restaurant.copy()
                    restaurants.append(restaurant_copy)
    
    # Pre-allocate attractions to days to ensure even distribution
    attractions_by_day = [[] for _ in range(num_days)]
    for i, attraction in enumerate(attractions):
        day_index = i % num_days  # Round-robin distribution
        attractions_by_day[day_index].append(attraction)
    
    # Ensure each day has minimum attractions
    for day_idx in range(num_days):
        if len(attractions_by_day[day_idx]) < min_attractions_per_day:
            needed = min_attractions_per_day - len(attractions_by_day[day_idx])
            logger.warning(f"Day {day_idx + 1} needs {needed} more attractions")
    
    # Build itinerary with time slots
    import random
    from datetime import datetime, timedelta
    
    scheduled_places = []
    
    for day in range(1, num_days + 1):
        day_index = day - 1
        
        # Get pre-allocated attractions for this day
        day_attractions = attractions_by_day[day_index]
        
        # Skip if no places for this day (should not happen with pre-allocation)
        if not day_attractions and not restaurants:
            logger.warning(f"No places available for day {day}")
            break
            
        current_time = datetime.strptime("08:00", "%H:%M")
        end_of_day = datetime.strptime("21:00", "%H:%M")
        
        day_schedule = []
        places_visited_today = 0
        attraction_index = 0
        
        # Schedule activities for this day
        # Aim for: breakfast spot (optional) → attractions → lunch → attractions → dinner
        for i in range(len(day_attractions) + 2):  # +2 for lunch and dinner
            if current_time >= end_of_day:
                break
            
            # Determine activity type based on time
            if current_time.hour >= 12 and current_time.hour < 13 and places_visited_today > 0:
                # Lunch time
                if restaurants:
                    place = restaurants.pop(0)
                    duration = timedelta(hours=1)
                    place["activity_type"] = "restaurant"
                    place["meal_type"] = "lunch"
                else:
                    continue
            elif current_time.hour >= 18 and current_time.hour < 20 and places_visited_today >= 2:
                # Dinner time
                if restaurants:
                    place = restaurants.pop(0)
                    duration = timedelta(hours=1, minutes=30)
                    place["activity_type"] = "restaurant"
                    place["meal_type"] = "dinner"
                else:
                    continue
            else:
                # Tourist attraction - use pre-allocated attractions
                if attraction_index < len(day_attractions):
                    place = day_attractions[attraction_index]
                    attraction_index += 1
                    # Random duration between 1-2 hours
                    duration = timedelta(hours=1, minutes=random.choice([0, 30, 60]))
                    place["activity_type"] = "attraction"
                    places_visited_today += 1
                else:
                    break
            
            # Add time information
            place["day"] = day
            place["start_time"] = current_time.strftime("%H:%M")
            current_time += duration
            place["end_time"] = current_time.strftime("%H:%M")
            
            day_schedule.append(place)
            
            # Add travel time between activities (15-30 mins)
            current_time += timedelta(minutes=random.choice([15, 20, 30]))
        
        scheduled_places.extend(day_schedule)
        
        logger.info(f"Day {day} scheduled: {len(day_schedule)} activities ({places_visited_today} attractions)")
    
    return scheduled_places


async def _translate_components_to_english(components: list) -> list:
    """Translate place data in components to English.
    
    Translates Korean text in: name, category, description, address
    Preserves: coordinates, times, ratings, URLs, phone numbers, all structure
    
    Args:
        components: List of component objects with place data
        
    Returns:
        Components with translated English text
    """
    try:
        # Collect all places that need translation
        all_places = []
        for component in components:
            if component.get("type") in ["trip_plan_day_schedule", "places_list"]:
                data = component.get("data", {})
                places = data.get("places", [])
                all_places.extend(places)
        
        if not all_places:
            return components
        
        logger.info(f"Translating {len(all_places)} places to English")
        
        # Batch translate all text fields
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # Prepare translation batch
        texts_to_translate = []
        for place in all_places:
            # Collect Korean text fields
            name = place.get("name", "")
            category = place.get("category", "")
            address = place.get("address", "")
            road_address = place.get("road_address", "")
            
            # Create translation request
            if name or category or address:
                texts_to_translate.append({
                    "name": name,
                    "category": category,
                    "address": address,
                    "road_address": road_address
                })
        
        # Translate using LLM in batch
        translation_prompt = f"""Translate the following Korean place information to English. Return ONLY a JSON array with the same structure.

For each place, translate:
- name: place name to English
- category: category to English (e.g., "여행,명소>궁궐" -> "Travel & Attractions > Palace")
- address: translate city/district names but keep street numbers and building names
- road_address: same as address

Keep the exact same JSON structure. Return valid JSON array only.

Places to translate:
{texts_to_translate[:10]}"""  # Limit to 10 places per batch for token limits
        
        messages = [
            SystemMessage(content="You are a professional translator specializing in Korean to English translation for travel information."),
            HumanMessage(content=translation_prompt)
        ]
        
        response = await llm.ainvoke(messages)
        translated_text = response.content.strip()
        
        # Parse translated JSON
        import json
        import re
        
        # Extract JSON array from response
        json_match = re.search(r'\[.*\]', translated_text, re.DOTALL)
        if json_match:
            translated_data = json.loads(json_match.group())
            
            # Map translations back to places
            for i, place in enumerate(all_places[:len(translated_data)]):
                if i < len(translated_data):
                    trans = translated_data[i]
                    if trans.get("name"):
                        place["name"] = trans["name"]
                    if trans.get("category"):
                        place["category"] = trans["category"]
                    if trans.get("address"):
                        place["address"] = trans["address"]
                    if trans.get("road_address"):
                        place["road_address"] = trans["road_address"]
            
            logger.info(f"Successfully translated {len(translated_data)} places to English")
        else:
            logger.warning("Could not parse translation response, using original Korean text")
        
        return components
        
    except Exception as e:
        logger.error(f"Translation failed: {e}, returning original components")
        return components


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
    
    # Handle casual conversation responses
    if state.get("intent_type") == "conversation" and state.get("rag_answer"):
        logger.info("Generating conversation response")
        
        state["final_response"] = response_formatter.format_simple_message(
            message=state["rag_answer"],
            actions_taken=state["actions_taken"],
            next_suggestions=state.get("next_suggestions", [])
        )
        
        logger.info("Conversation response generated")
        return state
    
    # Handle RAG query results
    if state.get("rag_answer"):
        logger.info("Generating RAG response with citations")
        
        rag_answer = state["rag_answer"]
        cited_sources = state.get("rag_cited_sources", [])
        
        # Format citations for UI
        citations = []
        for idx, source in enumerate(cited_sources, 1):
            citation = {
                "id": source.get("id"),
                "excerpt": source.get("doc", "")[:200] + "..." if len(source.get("doc", "")) > 200 else source.get("doc", ""),
                "metadata": source.get("metadata", {}),
                "full_metadata": source.get("full_metadata", {})
            }
            citations.append(citation)
        
        # Create travel_knowledge component
        component = {
            "type": "travel_knowledge",
            "data": {
                "answer": rag_answer,
                "citations": citations,
                "query": state["user_message"],
                "retrieved_count": len(state.get("rag_documents", []))
            }
        }
        
        # Get next suggestions
        next_suggestions = state.get("next_suggestions", [])
        if not next_suggestions:
            next_suggestions = [
                "Tell me more",
                "Find related places",
                "Plan my itinerary"
            ]
        
        state["final_response"] = {
            "message": "Here's what I found about your question:",
            "message_type": "travel_knowledge",
            "components": [component],
            "actions_taken": state["actions_taken"],
            "next_suggestions": next_suggestions
        }
        
        logger.info(f"RAG response generated with {len(citations)} citations")
        return state
    
    # Handle place search results
    if state["places_found"]:
        places = state["places_found"]
        request_type = state.get("request_type", "suggest_places")
        num_days = state.get("num_days", 1)
        destination = state.get("destination", "your destination")
        user_lang = state.get("user_language", "en")
        
        logger.info(f"Generating response: request_type={request_type}, num_places={len(places)}, num_days={num_days}")
        
        if request_type == "trip_planning":
            # TRIP PLANNING RESPONSE
            message = f"I've created a {num_days}-day itinerary for {destination} with {len(places)} activities including meals and attractions!"
            
            # Group places by day for trip planning
            days_schedule = {}
            for place in places:
                day = place.get("day", 1)
                if day not in days_schedule:
                    days_schedule[day] = []
                days_schedule[day].append(place)
            
            # Create trip planning component with all places
            components = [{
                "type": "trip_planning",
                "data": {
                    "destination": destination,
                    "num_days": num_days,
                    "travel_dates": state.get("travel_dates"),
                    "places": places,  # All places with day/time info
                    "days_schedule": {str(day): day_places for day, day_places in days_schedule.items()}
                }
            }]
            
            next_suggestions = [
                "Modify itinerary",
                "Add more places",
                "Get directions",
                "Save trip plan"
            ]
            
            # Translate components to English
            translated_components = await _translate_components_to_english(components)
            
            state["final_response"] = {
                "message": message,
                "message_type": "trip_planning",
                "components": translated_components,
                "actions_taken": state["actions_taken"],
                "next_suggestions": next_suggestions
            }
        else:
            # SUGGEST PLACES RESPONSE (Original format)
            message = f"I found {len(places)} amazing places in {destination} that match your preferences! These include top-rated restaurants, cultural attractions, and more."
            
            next_suggestions = [
                "Add a place to itinerary",
                "Get directions",
                "Search nearby attractions",
                "Create complete trip plan"
            ]
            
            # Format response first
            formatted_response = response_formatter.format_places_response(
                message=message,
                places=places,
                actions_taken=state["actions_taken"],
                next_suggestions=next_suggestions
            )
            
            # Translate components to English
            components = formatted_response.get("components", [])
            translated_components = await _translate_components_to_english(components)
            formatted_response["components"] = translated_components
            
            state["final_response"] = formatted_response
    else:
        # No results found
        message = "I couldn't find any places matching your request. Could you provide more details or try a different search?"
        
        user_lang = state.get("user_language", "en")
        if user_lang != "en":
            message = await language_detector.translate_to_language(message, user_lang)
        
        state["final_response"] = response_formatter.format_simple_message(
            message=message,
            actions_taken=state["actions_taken"],
            next_suggestions=["Try a different search", "Ask for recommendations"]
        )
    
    logger.info("Response generated successfully")
    return state


def _get_date_for_day(travel_dates: dict, day_num: int) -> str:
    """Calculate the date for a specific day number."""
    if not travel_dates or not travel_dates.get("start"):
        return f"Day {day_num}"
    
    try:
        from datetime import datetime, timedelta
        start_str = str(travel_dates["start"]).replace('/', '-')
        start_date = datetime.fromisoformat(start_str)
        target_date = start_date + timedelta(days=day_num - 1)
        return target_date.strftime("%Y-%m-%d")
    except:
        return f"Day {day_num}"


async def handle_rag_query(state: AgentState) -> AgentState:
    """Handle RAG queries for travel knowledge (culture, history, tips, insights).
    
    This node processes queries about cultural information, historical context,
    travel tips, and local insights using the RAG pipeline:
    
    Flow:
    1. Detect query language (Korean or other)
    2. If not Korean, translate to Korean for RAG search
    3. Embed the Korean query
    4. Search vector database (Korean documents)
    5. Rerank results
    6. Generate answer in Korean from Korean context
    7. If original query was not Korean, translate answer to English
    
    Note: Uses LATEST user message only, conversation history is just context.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with RAG results
    """
    logger.info("Handling RAG query for travel knowledge")
    
    original_query = state["user_message"]  # Latest message only
    destination = state.get("destination", "")
    
    try:
        # Step 1: Detect language of the query
        detected_lang = language_detector.detect_language(original_query)
        logger.info(f"Detected query language: {detected_lang}")
        
        # Step 2: Translate to Korean if needed (for better RAG with Korean documents)
        if detected_lang == "ko":
            query_for_rag = original_query
            logger.info("Using original Korean query for RAG")
        else:
            logger.info("Translating query to Korean for RAG")
            query_for_rag = await language_detector.translate_to_korean(original_query)
            logger.info(f"Translated query: {query_for_rag}")
        
        # Step 3: Generate query embedding
        logger.info("Step 1: Generating query embedding")
        query_embedding = await embed_query.ainvoke({"query": query_for_rag})
        state["actions_taken"].append("generated_embedding")
        
        # Step 4: Search vector database
        logger.info("Step 2: Searching vector database")
        
        # Note: Not using location filters since our documents are general travel info
        # Documents don't have location metadata set
        search_results = await search_vector_db.ainvoke({
            "query_embedding": query_embedding,
            "top_k": settings.RAG_TOP_K,
            "filters": None  # No filters for now
        })
        
        state["rag_documents"] = search_results
        state["actions_taken"].append(f"retrieved_{len(search_results)}_documents")
        logger.info(f"Retrieved {len(search_results)} documents from vector DB")
        
        if not search_results:
            logger.warning("No documents found in vector DB")
            no_result_msg = (
                "I don't have specific information about that in my knowledge base yet. "
                "However, I can help you find places to visit or plan your itinerary!"
            )
            # Return in original language
            if detected_lang == "ko":
                no_result_msg = await language_detector.translate_to_korean(no_result_msg)
            
            state["rag_answer"] = no_result_msg
            state["rag_cited_sources"] = []
            return state
        
        # Step 5: Rerank documents for relevance
        logger.info("Step 3: Reranking documents")
        rerank_result = await rerank_documents.ainvoke({
            "query": query_for_rag,  # Use Korean query for reranking
            "documents": search_results,
            "max_tokens": settings.RAG_MAX_TOKENS
        })
        
        state["actions_taken"].append("reranked_documents")
        
        # Extract reranked answer and citations (in Korean)
        rag_answer_korean = rerank_result.get("result", "")
        state["rag_cited_sources"] = rerank_result.get("cited_documents", [])
        
        logger.info(f"RAG answer generated with {len(state['rag_cited_sources'])} cited sources")
        
        # Step 6: Translate answer based on original query language
        if detected_lang == "ko":
            # Original query was Korean -> return Korean answer
            state["rag_answer"] = rag_answer_korean
            logger.info("Keeping answer in Korean (original query was Korean)")
        else:
            # Original query was not Korean -> translate answer to English
            logger.info("Translating RAG answer from Korean to English")
            state["rag_answer"] = await language_detector.translate_to_language(rag_answer_korean, "en")
            state["actions_taken"].append("translated_answer_to_english")
        
        # Step 7: Fetch full metadata for cited documents
        logger.info("Step 4: Enriching cited sources with metadata")
        for source in state["rag_cited_sources"]:
            doc_id = source.get("metadata", {}).get("document_id")
            if doc_id:
                metadata = await fetch_document_metadata.ainvoke({"document_id": doc_id})
                if metadata:
                    source["full_metadata"] = metadata
        
        state["actions_taken"].append("enriched_citations")
        
        # Add suggested follow-up queries if available
        suggested_queries = rerank_result.get("suggested_queries", [])
        if suggested_queries:
            state["next_suggestions"] = suggested_queries[:3]  # Limit to 3 suggestions
        
        logger.info("RAG query handling completed successfully")
        
    except Exception as e:
        logger.error(f"Error handling RAG query: {e}", exc_info=True)
        state["actions_taken"].append("rag_query_failed")
        
        error_msg = (
            "I encountered an issue while searching for that information. "
            "Please try asking in a different way, or I can help you find places to visit instead!"
        )
        
        # Return error in original language
        detected_lang = language_detector.detect_language(original_query)
        if detected_lang == "ko":
            error_msg = await language_detector.translate_to_korean(error_msg)
        
        state["rag_answer"] = error_msg
        state["rag_cited_sources"] = []
    
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
            auth_token = state.get("auth_token")
            
            # Build references from places found
            references = []
            for place in state.get("places_found", [])[:5]:  # Limit to first 5 places
                if place.get("id"):
                    references.append({"type": "place", "id": place["id"]})
            
            await api_client.send_message(
                session_id=state["session_id"],
                message=message_content,
                auth_token=auth_token,
                from_role="assistant",
                message_type="text",
                metadata={
                    "model": settings.MODEL_NAME,
                    "actions_taken": state["actions_taken"],
                    "places_count": len(state.get("places_found", []))
                },
                references=references if references else None
            )
            
            state["actions_taken"].append("Response saved to database")
            logger.info("Response saved successfully")
    
    except Exception as e:
        logger.error(f"Error saving response: {e}")
        state["actions_taken"].append("Failed to save response")
    
    return state
