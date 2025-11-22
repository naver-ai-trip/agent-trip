# Traver - Naver AI-Powered Travel Planning Platform

**Traver** is an intelligent travel planning platform powered by Naver AI that handles research, planning, risk detection, booking, and coordination in one unified system.

Built with LangGraph and integrated with backend APIs, Traver provides personalized travel recommendations, creates intelligent itineraries, and offers expert cultural knowledge through AI-powered retrieval.

## What is Traver?

Traver is not just a chatbot - it's a comprehensive travel planning platform that:

🔍 **Researches** - AI-powered destination analysis and cultural knowledge  
📋 **Plans** - Intelligent itinerary generation with optimization  
⚠️ **Detects** - Risk assessment and safety recommendations  
🎫 **Books** - Integrated booking coordination (coming soon)  
🤝 **Coordinates** - Unified system with backend synchronization

## Features

### 1. Intelligent Intent Detection
- **Conversation Handler**: Warm greetings and suggestions for next actions
- **RAG Query Engine**: Cultural knowledge and historical information retrieval
- **Trip Planning**: AI-powered itinerary generation with research
- **Place Discovery**: Smart recommendations based on preferences
- **Context-Aware**: Extracts intent from latest message, preserves conversation history

### 2. RAG (Knowledge Retrieval) System
- **Naver Clova Embedding v2**: 1024-dimensional vector embeddings
- **Pinecone Vector Database**: Semantic search for cultural knowledge
- **Multilingual Support**: Korean documents with English/Korean Q&A
- **Citation System**: Answers with source attribution
- **Auto-Translation**: Translates queries for optimal search

### 3. Travel Planning & Recommendations
- **Place Search**: Search with automatic Korean translation
- **Nearby Search**: Find attractions, restaurants, and hotels by coordinates
- **Web Scraping**: Tourist information from VisitKorea
- **Automatic Trip Planning**: Complete itineraries with intelligent scheduling
- **Smart Recommendations**: AI-powered suggestions based on user preferences

### 4. Multilingual Support
- **Automatic Language Detection**: Detects Korean vs English
- **Korean Backend Integration**: Translates queries for optimal search
- **Response Translation**: Returns in user's preferred language
- **RAG Multilingual**: 
  - English query → Korean search → English answer
  - Korean query → Korean search → Korean answer

### 5. Image Translation (UI-Triggered)
- Agent recognizes image translation requests
- Triggers UI to open image upload interface
- Backend API handles actual translation

### 6. Context-Aware Conversations
- Maintains chat session context (destination, budget, interests, dates)
- Tracks conversation history through backend API
- Intent extracted from **latest message only**
- Conversation history provides context

## Architecture

### Traver's AI-Powered Workflow
```
User Message → Initialize Session → Route Request → Process Intent → Generate Response → Save
                                           ↓
                    ┌──────────────────────┼──────────────────────┐
                    ↓                      ↓                      ↓
            Conversation            RAG Knowledge           Planning/Discovery
         (casual chat)          (culture/history)         (itinerary/places)
```

**Intent Detection:**
1. **Conversation**: Greetings, general chat → Warm response + suggestions
2. **RAG Query**: Culture, history, tips → Knowledge base search + citations
3. **Trip Planning**: Plan, itinerary → AI-powered schedule generation
4. **Place Discovery**: Recommend, find → Smart place suggestions

### LangGraph Workflow Nodes
- **Initialize**: Load chat session context from backend
- **Route**: Detect intent from **latest message** (history = context)
- **Conversation**: Handle casual chat with LLM
- **RAG Query**: Search knowledge base with Naver Clova + Pinecone
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
