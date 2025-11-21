# AI-Powered Travel Planning Application

An intelligent travel planning agent built with LangGraph and integrated with Laravel backend APIs. This agent provides personalized travel recommendations, creates itineraries, and supports multilingual interactions.

## Features

### 1. Travel Planning & Recommendations
- **Place Search**: Search for places by text query with automatic Korean translation
- **Nearby Search**: Find attractions, restaurants, and hotels near specific coordinates
- **Web Scraping**: Scrape tourist information from VisitKorea website
- **Automatic Trip Planning**: Generate complete itineraries with scheduling
- **Smart Recommendations**: AI-powered suggestions based on user preferences

### 2. Multilingual Support
- **Automatic Language Detection**: Detects user's language from messages
- **Korean Backend Integration**: Translates queries to Korean for optimal backend search
- **Response Translation**: Returns responses in user's preferred language

### 3. Image Translation (UI-Triggered)
- Agent recognizes image translation requests
- Triggers UI to open image upload interface
- Backend API handles actual translation

### 4. Context-Aware Conversations
- Maintains chat session context (destination, budget, interests, travel dates)
- Tracks conversation history through backend API
- Stores all interactions in database

## Architecture

### LangGraph Workflow
```
Initialize Session → Route Request → Search & Plan → Generate Response → Save Response
```

**Nodes:**
- **Initialize**: Load chat session context from backend
- **Route**: Determine request type (search, planning, image translation)
- **Search & Plan**: Execute place searches and create travel plans
- **Generate**: Format responses with structured UI components
- **Save**: Store agent responses in backend database

### Project Structure
```
agent-trip/
├── src/
│   ├── config.py              # Configuration management
│   ├── main.py                # FastAPI application
│   ├── graph/
│   │   ├── agent.py           # LangGraph workflow
│   │   ├── nodes.py           # Agent nodes
│   │   ├── state.py           # State definition
│   │   └── response_formatter.py  # Response formatting
│   ├── tools/
│   │   └── place_tools.py     # Place search tools
│   └── utils/
│       ├── api_client.py      # Backend API client
│       ├── translator.py      # Language translation
│       └── logger.py          # Logging configuration
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container config
├── docker-compose.yml         # Docker Compose config
└── README.md                  # This file
```

## Setup

### Prerequisites
- Python 3.11+
- OpenAI API key
- Access to Laravel backend API

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/naver-ai-trip/agent-trip.git
cd agent-trip
```

2. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Configure environment**
```powershell
# Copy example env file
cp .env.example .env

# Edit .env and add your credentials
# BE_API_BASE=https://voyagenius.montserrat.id.vn
# OPENAI_API_KEY=your_key_here
```

5. **Run the application**
```powershell
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Deployment

### Build and Run
```powershell
# Build the image
docker build -t agent-trip .

# Run with docker-compose
docker-compose up -d
```

### Environment Variables
Create a `.env` file with:
```env
BE_API_BASE=https://voyagenius.montserrat.id.vn
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4o-mini
DEBUG=true
```

## API Endpoints

### Main Endpoints

#### POST /api/chat
Process user messages and return structured responses.

**Request:**
```json
{
  "session_id": 2,
  "message": "I want to visit historical palaces in Seoul",
  "trip_id": 4
}
```

**Response:**
```json
{
  "response": {
    "message": "I found 5 amazing places in Seoul...",
    "components": [
      {
        "type": "places_list",
        "data": {
          "places": [...]
        }
      }
    ],
    "actions_taken": ["Loaded session context", "Found 5 places"],
    "next_suggestions": ["Add place to itinerary", "Get directions"]
  },
  "session_id": 2
}
```

#### POST /api/chat/stream
Streaming version with Server-Sent Events (SSE).

**Request:** Same as `/api/chat`

**Response:** SSE stream with progress updates and final response

#### GET /health
Health check endpoint.

### Debug Endpoints (DEBUG=true only)

#### POST /api/debug/test-search?query=Seoul
Test place search functionality.

## Response Structure

### Places List Response
```json
{
  "message": "Natural language message",
  "components": [
    {
      "type": "places_list",
      "data": {
        "places": [
          {
            "name": "Place Name",
            "category": "Category",
            "address": "Full Address",
            "road_address": "Road Address",
            "latitude": 37.5652853,
            "longitude": 126.9808087,
            "rating": 4.7,
            "phone": "",
            "naver_link": "URL",
            "description": "",
            "business_hours": null
          }
        ]
      }
    }
  ],
  "actions_taken": ["Action 1", "Action 2"],
  "next_suggestions": ["Suggestion 1", "Suggestion 2"]
}
```

### Trip Plan Response
```json
{
  "message": "Your complete 7-day itinerary...",
  "components": [
    {
      "type": "trip_plan",
      "data": {
        "summary": {
          "destination": "Seoul, South Korea",
          "start_date": "2025-12-01",
          "end_date": "2025-12-07",
          "total_days": 7,
          "budget": "moderate",
          "interests": ["food", "culture", "history"]
        },
        "itinerary": [
          {
            "day": 1,
            "date": "2025-12-01",
            "time_start": "09:00",
            "time_end": "12:00",
            "activity_type": "visit",
            "place": {...}
          }
        ]
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
  "actions_taken": [...],
  "next_suggestions": [...]
}
```

## Backend API Integration

### Chat Session APIs
- `GET /api/chat-sessions/{id}` - Get session details and context
- `GET /api/chat-sessions/{id}/messages` - Get message history
- `POST /api/chat-sessions/{id}/messages` - Send message

### Place Search APIs
- `POST /api/places/search` - Search places by text
- `POST /api/places/search-nearby` - Search nearby places

### Session Context
The agent automatically loads:
- Destination
- Budget level
- User interests
- Travel dates
- Trip and user IDs

## Development

### Adding New Tools
Create tools in `src/tools/`:

```python
from langchain.tools import tool

@tool
async def my_new_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return result
```

### Adding New Nodes
Add nodes in `src/graph/nodes.py`:

```python
async def my_node(state: AgentState) -> AgentState:
    """Node description."""
    # Process state
    return state
```

Update graph in `src/graph/agent.py`.

### Logging
Logs are stored in:
- `logs/error.log` - Error logs
- `logs/debug.log` - Debug logs (DEBUG=true only)

## Future Enhancements

### Planned Features
1. **Hotels API Integration** - Price comparison and booking
2. **Flight API Integration** - Flight search and recommendations
3. **Weather API Integration** - Weather-based planning
4. **RAG System** - Cultural information and travel tips retrieval
5. **Improved Itinerary Optimization** - AI-powered scheduling

### Additional Capabilities
- Multi-day trip optimization
- Budget calculation and tracking
- Real-time availability checks
- User preference learning
- Social features integration

## Troubleshooting

### Common Issues

**ImportError for packages**
```powershell
pip install -r requirements.txt
```

**Language detection fails**
- googletrans uses public API, may have rate limits
- Falls back to English if detection fails

**Backend API connection errors**
- Verify BE_API_BASE in .env
- Check network connectivity
- Ensure backend is running

**OpenAI API errors**
- Verify OPENAI_API_KEY is set correctly
- Check API quota and billing
- Try different MODEL_NAME if needed

## License

This project is proprietary to Naver AI Trip.

## Support

For issues and questions, please contact the development team.
