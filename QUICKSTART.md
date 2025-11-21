# Quick Start Guide

## Initial Setup (One-time)

### 1. Run Setup Script
```powershell
.\setup.ps1
```

This will:
- Create virtual environment
- Install all dependencies
- Create `.env` file from template
- Set up logs directory

### 2. Configure Environment
Edit `.env` file and add your credentials:
```env
BE_API_BASE=https://voyagenius.montserrat.id.vn
OPENAI_API_KEY=sk-...your-key...
MODEL_NAME=gpt-4o-mini
DEBUG=true
```

## Running the Application

### Development Mode
```powershell
.\run.ps1
```

The server will start on `http://localhost:8000`

### Using Docker
```powershell
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Testing the API

### 1. Health Check
```powershell
curl http://localhost:8000/health
```

### 2. Test Chat Endpoint
```powershell
curl -X POST http://localhost:8000/api/chat `
  -H "Content-Type: application/json" `
  -d '{
    "session_id": 2,
    "message": "I want to visit Seoul",
    "trip_id": 4
  }'
```

### 3. Test Place Search (Debug Mode)
```powershell
curl -X POST "http://localhost:8000/api/debug/test-search?query=Seoul"
```

## Common Use Cases

### Simple Place Search
**User:** "Show me restaurants in Seoul"
- Agent searches backend API
- Returns list of restaurants with ratings
- Provides next action suggestions

### Trip Planning Request
**User:** "Create a 7-day itinerary for Seoul"
- Agent loads session context (dates, budget, interests)
- Searches for relevant places
- Generates complete itinerary with time slots
- Returns trip plan with accept button

### Image Translation Request
**User:** "Translate this image"
- Agent triggers UI image upload component
- Backend API handles actual translation
- Agent confirms action

### Multilingual Support
**User (in Korean):** "서울의 역사적인 장소를 보여주세요"
- Agent detects Korean language
- Searches backend with Korean query
- Returns response in Korean

## Project Structure Overview

```
src/
├── main.py              ← FastAPI server (start here)
├── config.py            ← Environment configuration
├── graph/
│   ├── agent.py         ← LangGraph workflow definition
│   ├── nodes.py         ← Agent processing nodes
│   ├── state.py         ← State management
│   └── response_formatter.py  ← UI component formatting
├── tools/
│   └── place_tools.py   ← Place search tools
└── utils/
    ├── api_client.py    ← Backend API client
    ├── translator.py    ← Language translation
    ├── trip_planner.py  ← Itinerary generation
    └── logger.py        ← Logging setup
```

## Development Workflow

### 1. Modify Agent Logic
Edit `src/graph/nodes.py` to change agent behavior

### 2. Add New Tools
Create new tools in `src/tools/` and add to graph

### 3. Test Changes
```powershell
# Run in debug mode
DEBUG=true python -m uvicorn src.main:app --reload
```

### 4. View Logs
```powershell
# Watch error logs
Get-Content logs\error.log -Wait

# Watch debug logs
Get-Content logs\debug.log -Wait
```

## Troubleshooting

### Virtual Environment Issues
```powershell
# Deactivate current environment
deactivate

# Remove and recreate
Remove-Item -Recurse -Force venv
.\setup.ps1
```

### Dependency Issues
```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <process_id> /F
```

## API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Next Steps

1. **Add RAG System**: Implement cultural information retrieval
2. **Integrate Flight API**: Add flight search capabilities  
3. **Add Weather API**: Include weather-based planning
4. **Optimize Itineraries**: Enhance AI trip planning logic

## Support

For questions or issues:
1. Check logs in `logs/` directory
2. Review README.md for detailed documentation
3. Contact development team

## Useful Commands

```powershell
# Format code
black src/

# Type checking (if needed)
mypy src/

# Run tests (when implemented)
pytest tests/

# Build Docker image
docker build -t agent-trip .

# Push to registry
docker tag agent-trip:latest registry.example.com/agent-trip:latest
docker push registry.example.com/agent-trip:latest
```
