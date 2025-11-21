"""Place search and recommendation tools."""

import random
import logging
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from crewai_tools import ScrapeWebsiteTool

logger = logging.getLogger(__name__)

from src.utils.api_client import api_client
from src.utils.translator import language_detector


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
        # Translate query to Korean for backend
        korean_query = language_detector.translate_to_korean(query)
        logger.info(f"Searching places with query: {query} (Korean: {korean_query})")
        
        # Search using backend API
        places = await api_client.search_places(korean_query)
        
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
        # Translate query to Korean if provided
        korean_query = None
        if query:
            korean_query = language_detector.translate_to_korean(query)
        
        logger.info(f"Searching nearby places at ({latitude}, {longitude}) with radius {radius}m")
        
        # Search using backend API
        places = await api_client.search_nearby_places(
            latitude=latitude,
            longitude=longitude,
            query=korean_query,
            radius=radius
        )
        
        # Add ratings to all places
        places_with_ratings = [add_rating_to_place(place) for place in places]
        
        logger.info(f"Found {len(places_with_ratings)} nearby places")
        return places_with_ratings
    
    except Exception as e:
        logger.error(f"Error searching nearby places: {e}")
        return []


@tool
async def scrape_korea_tourist_spots(region: Optional[str] = None) -> str:
    """Scrape tourist attractions from VisitKorea website for Korean regions.
    
    Args:
        region: Optional specific region to focus on
        
    Returns:
        Scraped content containing tourist spots information
    """
    try:
        logger.info("Scraping VisitKorea website for tourist spots")
        
        scraper = ScrapeWebsiteTool(
            website_url="https://english.visitkorea.or.kr/svc/whereToGo/allRgn/allRegionList.do?menuSn=216"
        )
        
        content = scraper.run()
        logger.info("Successfully scraped VisitKorea website")
        
        return content
    
    except Exception as e:
        logger.error(f"Error scraping VisitKorea: {e}")
        return ""


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
        logger.info(f"Getting place details for Korean name: {korean_name}")
        
        places = await api_client.search_places(korean_name)
        
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
