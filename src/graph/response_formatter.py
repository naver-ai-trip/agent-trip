"""Response formatting utilities for structured UI components."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Format agent responses into structured components for UI rendering."""
    
    @staticmethod
    def format_places_response(
        message: str,
        places: List[Dict[str, Any]],
        actions_taken: List[str],
        next_suggestions: List[str]
    ) -> Dict[str, Any]:
        """Format a response with places list component.
        
        Args:
            message: Main message to display
            places: List of place dictionaries
            actions_taken: List of actions the agent performed
            next_suggestions: List of suggested next actions
            
        Returns:
            Structured response dictionary
        """
        return {
            "message": message,
            "components": [
                {
                    "type": "places_list",
                    "data": {
                        "places": places
                    }
                }
            ],
            "actions_taken": actions_taken,
            "next_suggestions": next_suggestions
        }
    
    @staticmethod
    def format_trip_plan_response(
        message: str,
        itinerary: List[Dict[str, Any]],
        trip_summary: Dict[str, Any],
        actions_taken: List[str],
        next_suggestions: List[str]
    ) -> Dict[str, Any]:
        """Format a response with complete trip plan.
        
        Args:
            message: Main message to display
            itinerary: List of itinerary items with time slots and places
            trip_summary: Summary of the trip (dates, destination, etc.)
            actions_taken: List of actions the agent performed
            next_suggestions: List of suggested next actions
            
        Returns:
            Structured response dictionary
        """
        return {
            "message": message,
            "components": [
                {
                    "type": "trip_plan",
                    "data": {
                        "summary": trip_summary,
                        "itinerary": itinerary
                    }
                },
                {
                    "type": "action_button",
                    "data": {
                        "label": "Accept Trip Plan",
                        "action": "accept_trip",
                        "style": "primary"
                    }
                }
            ],
            "actions_taken": actions_taken,
            "next_suggestions": next_suggestions
        }
    
    @staticmethod
    def format_simple_message(
        message: str,
        actions_taken: List[str] = None,
        next_suggestions: List[str] = None
    ) -> Dict[str, Any]:
        """Format a simple text message response.
        
        Args:
            message: Message text
            actions_taken: Optional list of actions performed
            next_suggestions: Optional list of suggested next actions
            
        Returns:
            Structured response dictionary
        """
        return {
            "message": message,
            "components": [],
            "actions_taken": actions_taken or [],
            "next_suggestions": next_suggestions or []
        }
    
    @staticmethod
    def format_image_translation_trigger(
        message: str
    ) -> Dict[str, Any]:
        """Format a response that triggers image translation in UI.
        
        Args:
            message: Acknowledgment message
            
        Returns:
            Structured response with translation trigger
        """
        return {
            "message": message,
            "components": [
                {
                    "type": "image_translation_trigger",
                    "data": {
                        "action": "open_image_upload"
                    }
                }
            ],
            "actions_taken": ["Prepared image translation interface"],
            "next_suggestions": ["Upload an image with text to translate"]
        }
    
    @staticmethod
    def create_itinerary_item(
        day: int,
        date: str,
        time_start: str,
        time_end: str,
        place: Dict[str, Any],
        activity_type: str = "visit"
    ) -> Dict[str, Any]:
        """Create an itinerary item for a trip plan.
        
        Args:
            day: Day number in the trip
            date: Date string (YYYY-MM-DD)
            time_start: Start time (HH:MM)
            time_end: End time (HH:MM)
            place: Place dictionary with details
            activity_type: Type of activity (visit, meal, hotel, etc.)
            
        Returns:
            Itinerary item dictionary
        """
        return {
            "day": day,
            "date": date,
            "time_start": time_start,
            "time_end": time_end,
            "activity_type": activity_type,
            "place": place
        }
    
    @staticmethod
    def create_trip_summary(
        destination: str,
        start_date: str,
        end_date: str,
        total_days: int,
        budget: str = "moderate",
        interests: List[str] = None
    ) -> Dict[str, Any]:
        """Create a trip summary object.
        
        Args:
            destination: Destination name
            start_date: Trip start date (YYYY-MM-DD)
            end_date: Trip end date (YYYY-MM-DD)
            total_days: Total number of days
            budget: Budget level
            interests: List of interest categories
            
        Returns:
            Trip summary dictionary
        """
        return {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "budget": budget,
            "interests": interests or []
        }


# Global formatter instance
response_formatter = ResponseFormatter()
