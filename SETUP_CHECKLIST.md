# 🚀 Setup Checklist for AI Travel Agent

## ✅ Pre-Setup Verification

- [ ] Python 3.11 or higher installed
- [ ] Git installed and repository cloned
- [ ] OpenAI API account with credits
- [ ] Access to Laravel backend API (https://voyagenius.montserrat.id.vn)
- [ ] PowerShell available (for Windows)
- [ ] Internet connection for package installation

## 📦 Initial Setup (Run Once)

### Step 1: Environment Setup
```powershell
cd d:\github\agent-trip
.\setup.ps1
```

This script will:
- [ ] Create Python virtual environment (`venv/`)
- [ ] Install all dependencies from `requirements.txt`
- [ ] Create `.env` file from template
- [ ] Create `logs/` directory

### Step 2: Configure Environment Variables

Edit `.env` file with your credentials:

```env
# Backend API (already configured)
BE_API_BASE=https://voyagenius.montserrat.id.vn

# Your OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-your-actual-key-here

# Model Configuration
MODEL_NAME=gpt-4o-mini

# Development Settings
DEBUG=true
```

**Required Changes:**
- [ ] Replace `your_openai_api_key_here` with actual OpenAI API key
- [ ] Verify `BE_API_BASE` is correct
- [ ] Adjust `MODEL_NAME` if needed (gpt-4o-mini is recommended)

## 🏃 Running the Application

### Local Development

```powershell
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Run the server
.\run.ps1
```

Expected output:
```
Starting AI Travel Planning Agent...
Starting server on http://localhost:8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Server will be available at:
- [ ] http://localhost:8000
- [ ] http://localhost:8000/docs (API documentation)

### Using Docker

```powershell
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🧪 Testing the Setup

### Test 1: Health Check

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "debug": true
}
```

- [ ] Health check returns 200 OK
- [ ] Response contains `"status": "healthy"`

### Test 2: Debug Search (DEBUG mode only)

```powershell
curl -X POST "http://localhost:8000/api/debug/test-search?query=Seoul"
```

Expected:
- [ ] Returns list of places
- [ ] Each place has `name`, `address`, `latitude`, `longitude`, `rating`

### Test 3: Chat Endpoint

```powershell
curl -X POST http://localhost:8000/api/chat `
  -H "Content-Type: application/json" `
  -d '{
    "session_id": 2,
    "message": "Show me restaurants in Seoul",
    "trip_id": 4
  }'
```

Expected response structure:
```json
{
  "response": {
    "message": "...",
    "components": [...],
    "actions_taken": [...],
    "next_suggestions": [...]
  },
  "session_id": 2
}
```

- [ ] Returns 200 OK
- [ ] Contains `response` object
- [ ] Contains `components` array
- [ ] Places have ratings between 4.6-5.0

### Test 4: Run Test Script

```powershell
python test_agent.py
```

Expected:
- [ ] Runs without errors
- [ ] Shows agent responses
- [ ] Displays places found

### Test 5: Run Examples

```powershell
python examples.py
```

Expected:
- [ ] Runs 6 different examples
- [ ] Shows various agent capabilities
- [ ] Completes successfully

## 📊 Verify Logs

Check that logs are being created:

- [ ] `logs/error.log` exists (may be empty if no errors)
- [ ] `logs/debug.log` exists (in DEBUG mode)
- [ ] Logs show agent activity

View logs in real-time:
```powershell
Get-Content logs\debug.log -Wait
```

## 🔍 Common Issues & Solutions

### Issue: "Import could not be resolved"
**Solution:** IDE linting errors are normal before package installation. Run `.\setup.ps1` to install packages.

### Issue: "Module not found"
**Solution:**
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution:**
```powershell
# Find process
netstat -ano | findstr :8000

# Kill process (replace <PID>)
taskkill /PID <PID> /F
```

### Issue: "OpenAI API error"
**Solution:**
- [ ] Verify API key in `.env` is correct
- [ ] Check OpenAI account has credits
- [ ] Ensure no typos in API key

### Issue: "Backend API connection error"
**Solution:**
- [ ] Verify `BE_API_BASE` in `.env`
- [ ] Check internet connection
- [ ] Test backend URL in browser: https://voyagenius.montserrat.id.vn/api/health

### Issue: "Language translation error"
**Solution:**
- [ ] googletrans may have rate limits
- [ ] System falls back to English automatically
- [ ] Consider using paid translation API for production

## 📚 Documentation Quick Reference

| Document | Purpose |
|----------|---------|
| `README.md` | Complete documentation with API reference |
| `QUICKSTART.md` | Quick start guide for developers |
| `IMPLEMENTATION_SUMMARY.md` | Overview of implementation and features |
| `DEVELOPER_GUIDE.md` | How to extend and customize the agent |
| `examples.py` | Runnable code examples |
| `test_agent.py` | Testing utilities |

## 🎯 Next Steps After Setup

### For Testing:
1. [ ] Test all API endpoints using Postman or curl
2. [ ] Try different languages (English, Korean, etc.)
3. [ ] Test image translation request
4. [ ] Verify chat session management
5. [ ] Check log files for proper logging

### For Development:
1. [ ] Review `DEVELOPER_GUIDE.md` for extension patterns
2. [ ] Explore `examples.py` for usage patterns
3. [ ] Familiarize with LangGraph workflow in `src/graph/agent.py`
4. [ ] Understand state management in `src/graph/state.py`
5. [ ] Review tool implementations in `src/tools/place_tools.py`

### For Integration:
1. [ ] Test with actual UI integration
2. [ ] Verify response format matches UI expectations
3. [ ] Test streaming endpoint for real-time updates
4. [ ] Validate session_id and trip_id flow
5. [ ] Confirm message storage in backend database

### For Production Deployment:
1. [ ] Set `DEBUG=false` in `.env`
2. [ ] Configure CORS for production domains
3. [ ] Set up SSL/TLS certificates
4. [ ] Configure environment-specific settings
5. [ ] Set up monitoring and alerting
6. [ ] Configure log rotation and retention
7. [ ] Set up backup and recovery procedures
8. [ ] Implement rate limiting
9. [ ] Add authentication middleware
10. [ ] Performance testing and optimization

## 🔐 Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] API keys are not committed to repository
- [ ] CORS is configured for specific domains (production)
- [ ] Rate limiting is enabled
- [ ] Input validation is in place
- [ ] Error messages don't expose sensitive info
- [ ] Logs don't contain sensitive data
- [ ] HTTPS is enforced (production)

## 📈 Performance Checklist

- [ ] Response times are acceptable (< 3 seconds)
- [ ] Backend API calls are efficient
- [ ] LLM calls are optimized
- [ ] Caching is implemented where appropriate
- [ ] Database queries are optimized
- [ ] No memory leaks detected
- [ ] Resource usage is within limits

## ✨ Feature Completeness

### Currently Implemented:
- [x] Place search by text
- [x] Nearby place search
- [x] Web scraping (VisitKorea)
- [x] Language detection and translation
- [x] Chat session management
- [x] Response formatting for UI
- [x] Message storage in backend
- [x] Random rating generation
- [x] Image translation trigger
- [x] Streaming responses
- [x] Structured UI components

### Planned (Future):
- [ ] Hotels API integration
- [ ] Flight API integration
- [ ] Weather API integration
- [ ] RAG system for cultural information
- [ ] Complete automatic trip planning
- [ ] Budget calculation
- [ ] Itinerary optimization
- [ ] Real-time availability checks
- [ ] User preference learning

## 📝 Deployment Environments

### Development
- [ ] Local machine setup complete
- [ ] Debug mode enabled
- [ ] All features working
- [ ] Tests passing

### Staging
- [ ] Docker container built
- [ ] Environment variables configured
- [ ] Backend API accessible
- [ ] Full integration testing done

### Production
- [ ] Debug mode disabled
- [ ] HTTPS configured
- [ ] Monitoring enabled
- [ ] Backup configured
- [ ] Performance optimized
- [ ] Security hardened

## 🎉 Completion Verification

All systems operational when:
- [ ] Server starts without errors
- [ ] Health check returns 200 OK
- [ ] Place search returns results
- [ ] Chat endpoint processes messages
- [ ] Responses saved to backend
- [ ] Logs are generated properly
- [ ] All tests pass
- [ ] Documentation reviewed
- [ ] Team trained on usage

---

## Support

If you encounter issues:
1. Check logs in `logs/` directory
2. Review troubleshooting section in `QUICKSTART.md`
3. Verify all checklist items above
4. Contact development team

## Success Criteria

✅ **Setup is successful when:**
- Server runs without errors
- API endpoints respond correctly
- Backend integration works
- Logs show agent activity
- Tests complete successfully
- Documentation is clear

**You're ready to go! 🚀**
