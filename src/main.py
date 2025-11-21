"""FastAPI application for the AI Travel Agent."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

from src.graph.agent import agent_graph
from src.graph.state import AgentState
from src.config import settings


# Create FastAPI app
app = FastAPI(
    title="AI Travel Planning Agent",
    description="LangGraph-powered travel planning assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: int
    message: str
    trip_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: Dict[str, Any]
    session_id: int


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "ok",
        "service": "AI Travel Planning Agent",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "debug": settings.DEBUG
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for processing user messages.
    
    Args:
        request: Chat request with session_id and message
        
    Returns:
        Structured response for UI rendering
    """
    logger.info(f"Received chat request for session {request.session_id}")
    
    try:
        # Initialize state
        initial_state: AgentState = {
            "messages": [],
            "session_id": request.session_id,
            "trip_id": request.trip_id,
            "user_message": request.message,
            "places_found": [],
            "actions_taken": [],
            "next_suggestions": [],
            "iteration_count": 0,
            "user_language": "en",
            "trigger_image_translation": False
        }
        
        # Execute the agent graph
        result = await agent_graph.ainvoke(initial_state)
        
        # Extract final response
        final_response = result.get("final_response", {
            "message": "I'm processing your request. Please try again.",
            "components": [],
            "actions_taken": [],
            "next_suggestions": []
        })
        
        logger.info(f"Chat request completed for session {request.session_id}")
        
        return ChatResponse(
            response=final_response,
            session_id=request.session_id
        )
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint for real-time responses.
    
    Args:
        request: Chat request with session_id and message
        
    Returns:
        Server-Sent Events stream
    """
    logger.info(f"Received streaming chat request for session {request.session_id}")
    
    async def event_generator():
        """Generate SSE events for streaming response."""
        try:
            # Initialize state
            initial_state: AgentState = {
                "messages": [],
                "session_id": request.session_id,
                "trip_id": request.trip_id,
                "user_message": request.message,
                "places_found": [],
                "actions_taken": [],
                "next_suggestions": [],
                "iteration_count": 0,
                "user_language": "en",
                "trigger_image_translation": False
            }
            
            # Stream through graph execution
            async for event in agent_graph.astream(initial_state):
                # Extract node name and state
                for node_name, node_state in event.items():
                    # Send progress updates
                    yield f"data: {json.dumps({'type': 'progress', 'node': node_name})}\n\n"
                    
                    # Send partial results if available
                    if node_name == "generate" and node_state.get("final_response"):
                        yield f"data: {json.dumps({'type': 'response', 'data': node_state['final_response']})}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.post("/api/debug/test-search")
async def test_search(query: str):
    """Debug endpoint to test place search functionality.
    
    Args:
        query: Search query
        
    Returns:
        Search results
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Debug endpoints disabled")
    
    from src.tools.place_tools import search_places_by_text
    
    try:
        results = await search_places_by_text.ainvoke({"query": query})
        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
