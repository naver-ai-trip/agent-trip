"""Place search and recommendation tools."""

import random
import logging
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from crewai_tools import ScrapeWebsiteTool

logger = logging.getLogger(__name__)

from src.utils.api_client import api_client
from src.utils.translator import language_detector
from src.utils.context import get_auth_token


def generate_random_rating(min_rating: float = 4.6, max_rating: float = 5.0) -> float:
    """Generate a random rating between min and max.
    
    Args:
        min_rating: Minimum rating value
        max_rating: Maximum rating value
        
    Returns:
        Random rating rounded to 1 decimal place
    """
    rating = random.uniform(min_rating, max_rating)
    return round(rating, 1)


def add_rating_to_place(place: Dict[str, Any]) -> Dict[str, Any]:
    """Add a random rating to a place if it doesn't have one.
    
    Args:
        place: Place dictionary
        
    Returns:
        Place dictionary with rating added
    """
    if "rating" not in place or place.get("rating") is None:
        place["rating"] = generate_random_rating()
    return place


@tool
async def search_places_by_text(query: str) -> List[Dict[str, Any]]:
    """Search for places using a text query. Translates query to Korean for better results.
    
    Args:
        query: Search query in any language (e.g., "Seoul restaurants", "Tokyo Tower")
        
    Returns:
        List of places with details including name, address, coordinates, rating, etc.
    """
    try:
        # Get auth token from context
        auth_token = get_auth_token()
        if not auth_token:
            logger.error("No auth token available in context")
            return []
        
        # Translate query to Korean for backend
        korean_query = await language_detector.translate_to_korean(query)
        logger.info(f"Searching places with query: {query} (Korean: {korean_query})")
        
        # Search using backend API
        places = await api_client.search_places(korean_query, auth_token)
        
        # Add ratings to all places
        places_with_ratings = [add_rating_to_place(place) for place in places]
        
        logger.info(f"Found {len(places_with_ratings)} places for query: {query}")
        return places_with_ratings
    
    except Exception as e:
        logger.error(f"Error searching places: {e}")
        return []


@tool
async def search_nearby_places(
    latitude: float,
    longitude: float,
    query: Optional[str] = None,
    radius: int = 5000
) -> List[Dict[str, Any]]:
    """Search for nearby places around specific coordinates.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        query: Optional search query (e.g., "restaurant", "hotel")
        radius: Search radius in meters (max 10000, default 5000)
        
    Returns:
        List of nearby places with details
    """
    try:
        # Get auth token from context
        auth_token = get_auth_token()
        if not auth_token:
            logger.error("No auth token available in context")
            return []
        
        # Translate query to Korean if provided
        korean_query = None
        if query:
            korean_query = await language_detector.translate_to_korean(query)
        
        logger.info(f"Searching nearby places at ({latitude}, {longitude}) with radius {radius}m")
        
        # Search using backend API
        places = await api_client.search_nearby_places(
            latitude=latitude,
            longitude=longitude,
            query=korean_query,
            radius=radius,
            auth_token=auth_token
        )
        
        # Add ratings to all places
        places_with_ratings = [add_rating_to_place(place) for place in places]
        
        logger.info(f"Found {len(places_with_ratings)} nearby places")
        return places_with_ratings
    
    except Exception as e:
        logger.error(f"Error searching nearby places: {e}")
        return []


@tool
async def scrape_korea_tourist_spots(region: Optional[str] = None) -> List[Dict[str, Any]]:
    """Scrape and extract tourist attractions from VisitKorea website for Korean regions.
    Uses AI to intelligently extract structured information about tourist spots including
    names, descriptions, locations, and categories.
    
    Args:
        region: Optional specific region to focus on (e.g., "Seoul", "Busan", "Jeju")
        
    Returns:
        List of tourist spots with structured information (name, description, location, category)
    """
    try:
        logger.info(f"Scraping VisitKorea website for tourist spots{f' in {region}' if region else ''}")
        
        # Scrape the website
        scraper = ScrapeWebsiteTool(
            website_url="https://english.visitkorea.or.kr/svc/whereToGo/allRgn/allRegionList.do?menuSn=216"
        )
        
        raw_content = scraper.run()
        
        # Use LLM to extract structured tourist information
        from langchain_openai import ChatOpenAI
        from src.config import settings
        
        llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        extraction_prompt = f"""You are a travel data extraction expert. Extract tourist attractions from the following website content.

Website Content:
{raw_content[:8000]}  # Limit content to avoid token limits

Instructions:
1. Extract tourist spots, attractions, and destinations
2. For each place, identify: name, brief description, location/region, category (e.g., palace, temple, nature, shopping, entertainment)
3. Focus on {region if region else "all regions in Korea"}
4. Return ONLY valid JSON array format, no additional text

Return format:
[
  {{
    "name": "Place name in English",
    "korean_name": "한글 이름 (if available)",
    "description": "Brief description",
    "location": "City/Region",
    "category": "tourist_attraction/temple/palace/nature/shopping/entertainment",
    "highlights": ["highlight1", "highlight2"]
  }}
]

Extract at least 10-15 tourist spots if available."""

        response = await llm.ainvoke(extraction_prompt)
        
        # Parse the LLM response
        import json
        import re
        
        content = response.content.strip()
        
        # Try to extract JSON array from response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            tourist_spots = json.loads(json_str)
            
            # Add random ratings to each spot
            for spot in tourist_spots:
                spot["rating"] = generate_random_rating()
            
            logger.info(f"Successfully extracted {len(tourist_spots)} tourist spots from VisitKorea")
            return tourist_spots
        else:
            logger.warning("Could not parse JSON from LLM response")
            return []
    
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing extracted tourist data: {e}")
        return []
    except Exception as e:
        logger.error(f"Error scraping VisitKorea: {e}")
        return []


@tool
async def get_place_details_by_korean_name(korean_name: str) -> Dict[str, Any]:
    """Get detailed information about a place using its Korean name.
    
    This tool is useful when you have a Korean place name from web scraping
    and need to get accurate details from the backend.
    
    Args:
        korean_name: Korean name of the place (e.g., "경복궁")
        
    Returns:
        Place details dictionary or empty dict if not found
    """
    try:
        # Get auth token from context
        auth_token = get_auth_token()
        if not auth_token:
            logger.error("No auth token available in context")
            return {}
        
        logger.info(f"Getting place details for Korean name: {korean_name}")
        
        places = await api_client.search_places(korean_name, auth_token)
        
        if places:
            place = places[0]  # Get the first (most relevant) result
            place = add_rating_to_place(place)
            logger.info(f"Found place details for: {korean_name}")
            return place
        else:
            logger.warning(f"No place found for Korean name: {korean_name}")
            return {}
    
    except Exception as e:
        logger.error(f"Error getting place details: {e}")
        return {}


# Tool collection for LangGraph
place_search_tools = [
    search_places_by_text,
    search_nearby_places,
    scrape_korea_tourist_spots,
    get_place_details_by_korean_name
]
