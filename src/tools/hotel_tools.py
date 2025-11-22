"""Hotel search tools for finding accommodations."""

import httpx
import logging
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool

from src.config import settings

logger = logging.getLogger(__name__)


@tool
async def search_hotels_with_offers(
    latitude: float,
    longitude: float,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    radius: int = 20,
    radius_unit: str = "KM",
    room_quantity: int = 1,
    currency: str = "USD"
) -> Dict[str, Any]:
    """Search for hotels with available offers.
    
    Args:
        latitude: Latitude of the search location
        longitude: Longitude of the search location
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        adults: Number of adults (default: 2)
        radius: Search radius (default: 20)
        radius_unit: Unit for radius (default: KM)
        room_quantity: Number of rooms (default: 1)
        currency: Currency code (default: USD)
    
    Returns:
        Dictionary with hotels and offers data
    """
    url = f"{settings.BE_API_BASE}/hotels/search-with-offers"
    
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "radius": radius,
        "radius_unit": radius_unit,
        "adults": adults,
        "room_quantity": room_quantity,
        "currency": currency
    }
    
    logger.info(f"Searching hotels: lat={latitude}, lon={longitude}, check_in={check_in_date}, check_out={check_out_date}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Found {data.get('meta', {}).get('total_offers', 0)} hotel offers")
            return data
    
    except httpx.HTTPError as e:
        logger.error(f"Hotel search failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return {
            "data": {"offers": []},
            "meta": {"total_hotels": 0, "total_offers": 0},
            "error": str(e)
        }


@tool
async def get_location_coordinates(destination: str, auth_token: str) -> Optional[Dict[str, float]]:
    """Get latitude and longitude for a destination by searching for places.
    
    Args:
        destination: City or place name to search for
        auth_token: Authentication token for the backend API
    
    Returns:
        Dictionary with latitude and longitude, or None if not found
    """
    from src.utils.api_client import BackendAPIClient
    from src.utils.translator import language_detector
    
    # Clean destination: remove country suffix if present (e.g., "Seoul, South Korea" -> "Seoul")
    destination_clean = destination.split(',')[0].strip()
    
    logger.info(f"Getting coordinates for: {destination_clean} (original: {destination})")
    
    try:
        # Translate to Korean for better backend results
        korean_query = await language_detector.translate_to_korean(destination_clean)
        logger.info(f"Translated destination: {korean_query}")
        
        # Use BackendAPIClient to search
        api_client = BackendAPIClient()
        places = await api_client.search_places(korean_query, auth_token)
        
        if places and len(places) > 0:
            first_place = places[0]
            
            # Extract coordinates from place data
            lat = first_place.get("latitude") or first_place.get("y")
            lon = first_place.get("longitude") or first_place.get("x")
            
            if lat and lon:
                coords = {
                    "latitude": float(lat),
                    "longitude": float(lon)
                }
                logger.info(f"Found coordinates: {coords} for {destination_clean}")
                return coords
        
        logger.warning(f"No places found for: {destination_clean}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to get coordinates for {destination_clean}: {e}")
        return None


def format_hotel_offers_response(
    offers_data: Dict[str, Any],
    check_in_date: str,
    check_out_date: str,
    destination: str
) -> List[Dict[str, Any]]:
    """Format hotel offers data for UI component.
    
    Args:
        offers_data: Raw offers data from API
        check_in_date: Check-in date
        check_out_date: Check-out date
        destination: Destination name
    
    Returns:
        List of formatted hotel offer components
    """
    offers = offers_data.get("data", {}).get("offers", [])
    
    components = []
    
    for offer_group in offers:
        hotel_data = offer_group.get("hotel", {})
        hotel_offers = offer_group.get("offers", [])
        
        if not hotel_offers:
            continue
        
        # Format hotel information
        hotel_info = {
            "hotelId": hotel_data.get("hotelId"),
            "name": hotel_data.get("name"),
            "latitude": hotel_data.get("latitude"),
            "longitude": hotel_data.get("longitude")
        }
        
        # Format offers
        formatted_offers = []
        for offer in hotel_offers:
            formatted_offer = {
                "id": offer.get("id"),
                "checkInDate": offer.get("checkInDate"),
                "checkOutDate": offer.get("checkOutDate"),
                "rateCode": offer.get("rateCode"),
                "room": offer.get("room"),
                "guests": offer.get("guests"),
                "price": offer.get("price"),
                "policies": offer.get("policies")
            }
            formatted_offers.append(formatted_offer)
        
        component = {
            "type": "hotel_offers",
            "data": {
                "hotel": hotel_info,
                "offers": formatted_offers
            }
        }
        
        components.append(component)
    
    logger.info(f"Formatted {len(components)} hotel offer components")
    return components
