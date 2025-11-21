"""Enhanced trip planning with complete itinerary generation."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

from src.graph.response_formatter import response_formatter


class TripPlanner:
    """Advanced trip planning with itinerary generation."""
    
    @staticmethod
    def calculate_days(start_date: str, end_date: str) -> int:
        """Calculate number of days between dates.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Number of days
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return (end - start).days + 1
        except Exception as e:
            logger.error(f"Error calculating days: {e}")
            return 1
    
    @staticmethod
    def generate_time_slots() -> List[Dict[str, str]]:
        """Generate typical time slots for a day.
        
        Returns:
            List of time slot dictionaries
        """
        return [
            {"start": "09:00", "end": "12:00", "type": "morning_activity"},
            {"start": "12:00", "end": "14:00", "type": "lunch"},
            {"start": "14:00", "end": "17:00", "type": "afternoon_activity"},
            {"start": "17:00", "end": "19:00", "type": "evening_activity"},
            {"start": "19:00", "end": "21:00", "type": "dinner"},
        ]
    
    @staticmethod
    def categorize_place(category: str) -> str:
        """Categorize place for activity type.
        
        Args:
            category: Place category
            
        Returns:
            Activity type (visit, meal, hotel)
        """
        category_lower = category.lower()
        
        if any(food in category_lower for food in ["음식", "식당", "레스토랑", "카페"]):
            return "meal"
        elif any(stay in category_lower for stay in ["숙박", "호텔", "리조트"]):
            return "hotel"
        else:
            return "visit"
    
    @staticmethod
    def create_itinerary(
        places: List[Dict[str, Any]],
        start_date: str,
        end_date: str,
        destination: str,
        budget: str = "moderate",
        interests: List[str] = None
    ) -> Dict[str, Any]:
        """Create a complete trip itinerary.
        
        Args:
            places: List of places to include
            start_date: Trip start date
            end_date: Trip end date
            destination: Destination name
            budget: Budget level
            interests: User interests
            
        Returns:
            Complete trip plan with itinerary
        """
        total_days = TripPlanner.calculate_days(start_date, end_date)
        time_slots = TripPlanner.generate_time_slots()
        
        # Create trip summary
        trip_summary = response_formatter.create_trip_summary(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            budget=budget,
            interests=interests or []
        )
        
        # Build itinerary
        itinerary = []
        place_index = 0
        
        for day in range(1, total_days + 1):
            current_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day - 1)
            date_str = current_date.strftime("%Y-%m-%d")
            
            for slot in time_slots:
                if place_index >= len(places):
                    break
                
                place = places[place_index]
                activity_type = TripPlanner.categorize_place(place.get("category", ""))
                
                # Match activity type to time slot
                if slot["type"] == "lunch" or slot["type"] == "dinner":
                    # Find a restaurant
                    restaurant = next(
                        (p for i, p in enumerate(places[place_index:], place_index) 
                         if TripPlanner.categorize_place(p.get("category", "")) == "meal"),
                        place
                    )
                    itinerary_item = response_formatter.create_itinerary_item(
                        day=day,
                        date=date_str,
                        time_start=slot["start"],
                        time_end=slot["end"],
                        place=restaurant,
                        activity_type="meal"
                    )
                else:
                    # Regular activity
                    itinerary_item = response_formatter.create_itinerary_item(
                        day=day,
                        date=date_str,
                        time_start=slot["start"],
                        time_end=slot["end"],
                        place=place,
                        activity_type="visit"
                    )
                
                itinerary.append(itinerary_item)
                place_index += 1
        
        logger.info(f"Created itinerary with {len(itinerary)} items for {total_days} days")
        
        return {
            "summary": trip_summary,
            "itinerary": itinerary
        }


# Global planner instance
trip_planner = TripPlanner()
