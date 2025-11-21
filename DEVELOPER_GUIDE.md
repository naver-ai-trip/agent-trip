# Developer Guide: Extending the AI Travel Agent

This guide explains how to extend and customize the agent for new features.

## Table of Contents
1. [Adding New Tools](#adding-new-tools)
2. [Adding New Nodes](#adding-new-nodes)
3. [Modifying the Workflow](#modifying-the-workflow)
4. [Creating Custom Response Components](#creating-custom-response-components)
5. [Implementing RAG System](#implementing-rag-system)
6. [Adding New APIs](#adding-new-apis)

---

## Adding New Tools

Tools are functions the agent can call to perform specific tasks.

### Step 1: Create Tool Function

Create a new tool in `src/tools/` or extend existing files:

```python
# src/tools/flight_tools.py
from langchain.tools import tool
from typing import List, Dict, Any
from loguru import logger

@tool
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = None
) -> List[Dict[str, Any]]:
    """Search for flights between two locations.
    
    Args:
        origin: Departure city or airport code
        destination: Arrival city or airport code
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Optional return date for round trip
        
    Returns:
        List of flight options with prices and times
    """
    try:
        # Call your flight API here
        from src.utils.api_client import api_client
        
        flights = await api_client.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date
        )
        
        logger.info(f"Found {len(flights)} flights")
        return flights
    except Exception as e:
        logger.error(f"Flight search error: {e}")
        return []
```

### Step 2: Register Tool

Add to tool collection:

```python
# In src/tools/flight_tools.py
flight_tools = [
    search_flights,
    # Add more flight-related tools
]
```

### Step 3: Use in Node

Import and use in nodes:

```python
# In src/graph/nodes.py
from src.tools.flight_tools import search_flights

async def search_flights_node(state: AgentState) -> AgentState:
    """Search for flights based on user request."""
    
    flights = await search_flights.ainvoke({
        "origin": state.get("origin"),
        "destination": state.get("destination"),
        "departure_date": state.get("departure_date")
    })
    
    state["flights_found"] = flights
    return state
```

---

## Adding New Nodes

Nodes are processing steps in the LangGraph workflow.

### Step 1: Create Node Function

Add to `src/graph/nodes.py`:

```python
async def hotel_search_node(state: AgentState) -> AgentState:
    """Search for hotels in the destination.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with hotel results
    """
    logger.info("Searching for hotels")
    
    try:
        # Get parameters from state
        destination = state.get("destination")
        check_in = state.get("check_in_date")
        check_out = state.get("check_out_date")
        budget = state.get("budget")
        
        # Call hotel search API
        hotels = await search_hotels(
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            budget=budget
        )
        
        # Update state
        state["hotels_found"] = hotels
        state["actions_taken"].append(f"Found {len(hotels)} hotels")
        
        logger.info(f"Found {len(hotels)} hotels")
        
    except Exception as e:
        logger.error(f"Hotel search error: {e}")
        state["hotels_found"] = []
        state["actions_taken"].append("Hotel search failed")
    
    return state
```

### Step 2: Register in Graph

Update `src/graph/agent.py`:

```python
def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add your new node
    workflow.add_node("hotel_search", hotel_search_node)
    
    # Connect it in the workflow
    workflow.add_edge("search_plan", "hotel_search")
    workflow.add_edge("hotel_search", "generate")
    
    # ... rest of graph definition
```

### Step 3: Update State (if needed)

Add new fields to `src/graph/state.py`:

```python
class AgentState(MessagesState):
    # Existing fields...
    
    # New fields for hotels
    hotels_found: List[Dict[str, Any]] = []
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
```

---

## Modifying the Workflow

### Adding Conditional Routing

```python
# In src/graph/agent.py

def route_by_request_type(state: AgentState) -> str:
    """Route based on user request type."""
    
    user_msg = state["user_message"].lower()
    
    if "hotel" in user_msg:
        return "hotel_search"
    elif "flight" in user_msg:
        return "flight_search"
    elif "complete trip" in user_msg or "full itinerary" in user_msg:
        return "full_trip_planning"
    else:
        return "place_search"

# Add conditional edges
workflow.add_conditional_edges(
    "route",
    route_by_request_type,
    {
        "hotel_search": "hotel_search",
        "flight_search": "flight_search",
        "full_trip_planning": "trip_planning",
        "place_search": "search_plan"
    }
)
```

### Creating Parallel Paths

```python
from langgraph.graph import START, END

# Create parallel execution
workflow.add_node("search_places", search_places_node)
workflow.add_node("search_hotels", hotel_search_node)
workflow.add_node("search_flights", flight_search_node)
workflow.add_node("combine_results", combine_results_node)

# Both run in parallel from route
workflow.add_edge("route", "search_places")
workflow.add_edge("route", "search_hotels")
workflow.add_edge("route", "search_flights")

# All converge to combine
workflow.add_edge("search_places", "combine_results")
workflow.add_edge("search_hotels", "combine_results")
workflow.add_edge("search_flights", "combine_results")
```

---

## Creating Custom Response Components

### Step 1: Define Component Structure

In `src/graph/response_formatter.py`:

```python
@staticmethod
def format_hotel_results(
    message: str,
    hotels: List[Dict[str, Any]],
    actions_taken: List[str],
    next_suggestions: List[str]
) -> Dict[str, Any]:
    """Format hotel search results.
    
    Args:
        message: Description message
        hotels: List of hotel data
        actions_taken: Actions performed
        next_suggestions: Suggested next actions
        
    Returns:
        Formatted response for UI
    """
    return {
        "message": message,
        "components": [
            {
                "type": "hotel_list",
                "data": {
                    "hotels": hotels,
                    "filters": {
                        "price_range": True,
                        "star_rating": True,
                        "amenities": True
                    }
                }
            },
            {
                "type": "map_view",
                "data": {
                    "markers": [
                        {
                            "lat": hotel["latitude"],
                            "lng": hotel["longitude"],
                            "label": hotel["name"]
                        }
                        for hotel in hotels
                    ]
                }
            }
        ],
        "actions_taken": actions_taken,
        "next_suggestions": next_suggestions
    }
```

### Step 2: Use in Node

```python
async def generate_hotel_response(state: AgentState) -> AgentState:
    """Generate response with hotel results."""
    
    hotels = state["hotels_found"]
    
    if hotels:
        state["final_response"] = response_formatter.format_hotel_results(
            message=f"I found {len(hotels)} hotels matching your criteria!",
            hotels=hotels,
            actions_taken=state["actions_taken"],
            next_suggestions=["Book hotel", "Compare prices", "View on map"]
        )
    
    return state
```

---

## Implementing RAG System

### Step 1: Create RAG Tools

```python
# src/tools/rag_tools.py
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Dict, Any

# Initialize embeddings
embeddings = OpenAIEmbeddings()

@tool
async def search_cultural_info(
    query: str,
    country: str = None
) -> str:
    """Search cultural information and travel tips.
    
    Args:
        query: Search query
        country: Optional country filter
        
    Returns:
        Relevant cultural information
    """
    try:
        # Load vector store
        vectorstore = FAISS.load_local(
            "data/cultural_knowledge",
            embeddings
        )
        
        # Add country filter if provided
        if country:
            query = f"{country}: {query}"
        
        # Search
        docs = vectorstore.similarity_search(query, k=3)
        
        # Combine results
        results = "\n\n".join([doc.page_content for doc in docs])
        
        return results
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        return ""
```

### Step 2: Create Document Chunking

```python
# scripts/prepare_rag_data.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

def prepare_cultural_knowledge():
    """Prepare and embed cultural documents."""
    
    # Load your documents
    documents = [
        Document(
            page_content="South Korea has a rich cultural heritage...",
            metadata={"country": "South Korea", "category": "culture"}
        ),
        # Add more documents
    ]
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    # Create embeddings
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    # Save
    vectorstore.save_local("data/cultural_knowledge")
    print(f"Embedded {len(splits)} chunks")

if __name__ == "__main__":
    prepare_cultural_knowledge()
```

### Step 3: Integrate in Node

```python
async def enrich_with_cultural_info(state: AgentState) -> AgentState:
    """Enrich response with cultural information."""
    
    destination = state.get("destination")
    
    if destination:
        # Search for cultural info
        cultural_info = await search_cultural_info.ainvoke({
            "query": "travel tips and customs",
            "country": destination
        })
        
        # Add to state
        state["cultural_context"] = cultural_info
        state["actions_taken"].append("Retrieved cultural information")
    
    return state
```

---

## Adding New APIs

### Step 1: Extend API Client

```python
# In src/utils/api_client.py

class BackendAPIClient:
    # Existing methods...
    
    async def get_weather_forecast(
        self,
        location: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get weather forecast for location.
        
        Args:
            location: Location name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Weather forecast data
        """
        try:
            response = await self.client.get(
                "/api/weather/forecast",
                params={
                    "location": location,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved weather for {location}")
            return data.get("data", {})
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            raise
```

### Step 2: Create Tool Wrapper

```python
# src/tools/weather_tools.py
from src.utils.api_client import api_client

@tool
async def get_weather(
    location: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """Get weather forecast for travel planning."""
    
    forecast = await api_client.get_weather_forecast(
        location=location,
        start_date=start_date,
        end_date=end_date
    )
    
    return forecast
```

---

## Best Practices

### 1. Error Handling

Always wrap API calls and tool invocations:

```python
try:
    result = await some_api_call()
    state["actions_taken"].append("Successfully called API")
except Exception as e:
    logger.error(f"API call failed: {e}")
    state["actions_taken"].append("API call failed")
    state["errors"].append(str(e))
    # Provide fallback behavior
```

### 2. Logging

Log important steps:

```python
logger.info("Starting process")
logger.debug(f"State: {state}")
logger.warning("Unusual condition detected")
logger.error(f"Error occurred: {e}", exc_info=True)
```

### 3. State Management

Keep state clean and organized:

```python
# Good: Clear field names
state["hotels_found"] = hotels
state["hotel_search_completed"] = True

# Bad: Ambiguous fields
state["results"] = hotels
state["done"] = True
```

### 4. Type Hints

Use type hints for better IDE support:

```python
from typing import List, Dict, Any, Optional

async def my_function(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """Properly typed function."""
    pass
```

### 5. Testing

Create test cases:

```python
# tests/test_tools.py
import pytest
from src.tools.place_tools import search_places_by_text

@pytest.mark.asyncio
async def test_search_places():
    results = await search_places_by_text.ainvoke({"query": "Seoul"})
    assert len(results) > 0
    assert "name" in results[0]
    assert "rating" in results[0]
```

---

## Common Patterns

### Pattern 1: Conditional Tool Usage

```python
if user_wants_hotels:
    hotels = await search_hotels.ainvoke(params)
elif user_wants_flights:
    flights = await search_flights.ainvoke(params)
else:
    places = await search_places.ainvoke(params)
```

### Pattern 2: Data Enrichment

```python
# Get base data
places = await search_places(query)

# Enrich with additional info
for place in places:
    place["weather"] = await get_weather(place["location"])
    place["reviews"] = await get_reviews(place["id"])
```

### Pattern 3: Fallback Chain

```python
# Try primary source
result = await primary_api.search(query)

if not result:
    # Try secondary source
    result = await secondary_api.search(query)

if not result:
    # Try web scraping
    result = await scrape_web(query)

return result or []
```

---

## Debugging Tips

### 1. Enable Debug Logging

```env
DEBUG=true
```

### 2. View Graph Execution

```python
async for event in agent_graph.astream(state):
    print(f"Node: {list(event.keys())[0]}")
    print(f"State: {event}")
```

### 3. Test Individual Nodes

```python
from src.graph.nodes import search_and_plan

state = {"user_message": "Test", ...}
result = await search_and_plan(state)
print(result)
```

### 4. Check API Responses

```python
# Test backend API directly
from src.utils.api_client import api_client

result = await api_client.search_places("Seoul")
print(result)
```

---

## Deployment Checklist

- [ ] Set `DEBUG=false` in production
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable authentication
- [ ] Configure monitoring
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Use production-ready database
- [ ] Enable HTTPS
- [ ] Set resource limits
- [ ] Configure auto-scaling

---

## Getting Help

- Review `README.md` for API documentation
- Check `QUICKSTART.md` for common issues
- Run `examples.py` for usage patterns
- View logs in `logs/` directory
- Contact development team for support
