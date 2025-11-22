"""Backend API client for communicating with Laravel backend."""

import httpx
import logging
from typing import Dict, Any, List, Optional
from src.config import settings

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """Client for interacting with the Laravel backend API."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the backend API. Defaults to settings.BE_API_BASE
        """
        self.base_url = base_url or settings.BE_API_BASE
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get_chat_session(self, session_id: int, auth_token: str) -> Dict[str, Any]:
        """Get chat session details.
        
        Args:
            session_id: ID of the chat session
            auth_token: Bearer token for authentication
            
        Returns:
            Chat session data
        """
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = await self.client.get(
                f"/api/chat-sessions/{session_id}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved chat session {session_id}")
            return data.get("data", {})
        except Exception as e:
            logger.error(f"Error getting chat session {session_id}: {e}")
            raise
    
    async def get_chat_messages(
        self, 
        session_id: int,
        auth_token: str,
        page: int = 1
    ) -> Dict[str, Any]:
        """Get messages from a chat session.
        
        Args:
            session_id: ID of the chat session
            auth_token: Bearer token for authentication
            page: Page number for pagination
            
        Returns:
            Chat messages data with pagination
        """
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = await self.client.get(
                f"/api/chat-sessions/{session_id}/messages",
                params={"page": page},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved messages for session {session_id}")
            return data
        except Exception as e:
            logger.error(f"Error getting messages for session {session_id}: {e}")
            raise
    
    async def send_message(
        self,
        session_id: int,
        message: str,
        auth_token: str,
        from_role: str = "assistant",
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send a message to the chat session.
        
        Args:
            session_id: ID of the chat session
            message: Message content
            auth_token: Bearer token for authentication
            from_role: Role of the sender (user/assistant)
            message_type: Type of message (text/image/location)
            metadata: Additional metadata
            references: List of references with 'type' and 'id' fields
                       Example: [{"type": "place", "id": 123}]
            
        Returns:
            Created message data
        """
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            payload = {
                "content": message,
                "from_role": from_role,
                "message_type": message_type,
            }
            if metadata:
                payload["metadata"] = metadata
            if references:
                payload["references"] = references
                
            response = await self.client.post(
                f"/api/chat-sessions/{session_id}/messages",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Sent message to session {session_id}")
            return data.get("data", {})
        except Exception as e:
            logger.error(f"Error sending message to session {session_id}: {e}")
            raise
    
    async def search_places(self, query: str, auth_token: str) -> List[Dict[str, Any]]:
        """Search places by text query.
        
        Args:
            query: Search query text
            auth_token: Bearer token for authentication
            
        Returns:
            List of places matching the query
        """
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = await self.client.post(
                "/api/places/search",
                json={"query": query},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            places = data.get("data", [])
            logger.info(f"Found {len(places)} places for query: {query}")
            return places
        except Exception as e:
            logger.error(f"Error searching places for query '{query}': {e}")
            raise
    
    async def search_nearby_places(
        self,
        latitude: float,
        longitude: float,
        auth_token: str,
        query: Optional[str] = None,
        radius: int = 5000
    ) -> List[Dict[str, Any]]:
        """Search for nearby places by coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            auth_token: Bearer token for authentication
            query: Optional search query
            radius: Search radius in meters (max 10000)
            
        Returns:
            List of nearby places
        """
        try:
            # Ensure radius doesn't exceed maximum
            radius = min(radius, 10000)
            
            headers = {"Authorization": f"Bearer {auth_token}"}
            payload = {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius
            }
            if query:
                payload["query"] = query
                
            response = await self.client.post(
                "/api/places/search-nearby",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            places = data.get("data", [])
            logger.info(f"Found {len(places)} nearby places")
            return places
        except Exception as e:
            logger.error(f"Error searching nearby places: {e}")
            raise


# Global client instance
api_client = BackendAPIClient()
