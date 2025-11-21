# 🚀 Quick Start Guide - Run Me First!

## ✅ Prerequisites Check

Before running, ensure:
- [x] Python 3.11+ installed
- [x] All packages installed: `pip install -r requirements.txt`
- [x] `.env` file configured with API keys
- [x] Backend API accessible: https://voyagenius.montserrat.id.vn

---

## 🎯 Three Ways to Run

### 1️⃣ **Recommended: Direct Python** (Fastest)

```powershell
cd d:\github\agent-trip
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Access at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

### 2️⃣ **PowerShell Script** (Automated)

```powershell
.\run.ps1
```

This script will:
- Activate virtual environment (if exists)
- Check dependencies
- Start the server
- Open browser to API docs

---

### 3️⃣ **Docker** (Production-like)

```powershell
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

**Access at:** http://localhost:8000

---

## 🧪 Quick Test

### Test 1: Health Check
```powershell
# PowerShell
Invoke-RestMethod -Uri http://localhost:8000/health

# Or open in browser
start http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "debug": true
}
```

---

### Test 2: API Documentation
```powershell
start http://localhost:8000/docs
```

You should see **Swagger UI** with all endpoints:
- `GET /` - Welcome
- `GET /health` - Health check
- `POST /api/chat` - Chat endpoint
- `POST /api/chat/stream` - Streaming chat
- `POST /api/debug/test-search` - Debug search

---

### Test 3: Chat Endpoint (Using Python)

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/chat",
    json={
        "session_id": 1,
        "message": "Find tourist attractions in Seoul"
    }
)
print(response.json())
```

---

## 🐛 Troubleshooting

### Problem: Import Error
```
ModuleNotFoundError: No module named 'langchain'
```

**Solution:**
```powershell
pip install -r requirements.txt
```

---

### Problem: Port Already in Use
```
ERROR: [Errno 10048] error while attempting to bind on address
```

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /F /PID <PID>

# Or use different port
python -m uvicorn src.main:app --port 8001
```

---

### Problem: API Key Error
```
ValidationError: OPENAI_API_KEY
```

**Solution:**
1. Check `.env` file exists
2. Ensure `OPENAI_API_KEY=sk-...` is set
3. Restart the server

---

### Problem: Backend API Connection Error
```
Connection refused to https://voyagenius.montserrat.id.vn
```

**Solution:**
1. Check internet connection
2. Verify backend is running
3. Check firewall settings

---

## 📊 What's Running?

When the server starts successfully, you'll see:

```
INFO:     Will watch for changes in these directories: ['D:\\github\\agent-trip']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [PID] using WatchFiles
2025-11-22 01:07:18 | INFO     | root:setup_logging - Logging configured successfully
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Logs saved to:** `logs/app.log`

---

## 🔍 Monitoring Logs

### View Real-Time Logs
```powershell
Get-Content .\logs\app.log -Wait -Tail 50
```

### Search Logs
```powershell
Select-String -Path .\logs\app.log -Pattern "ERROR"
```

---

## 🎯 Next Steps After Running

1. **Test Health Endpoint**
   ```powershell
   curl http://localhost:8000/health
   ```

2. **Explore API Docs**
   ```powershell
   start http://localhost:8000/docs
   ```

3. **Test Chat Endpoint**
   - Use Swagger UI at `/docs`
   - Or use `curl`/`httpx`/Postman

4. **Check Logs**
   ```powershell
   cat .\logs\app.log
   ```

5. **Try Sample Requests**
   - Search for places
   - Create trip plans
   - Test multilingual support

---

## 📚 Documentation

- **README.md** - Project overview
- **QUICKSTART.md** - Detailed setup guide
- **DEVELOPER_GUIDE.md** - Development guidelines
- **DEPLOYMENT_SUCCESS.md** - Current status
- **IMPLEMENTATION_SUMMARY.md** - Technical details

---

## 💡 Pro Tips

### 1. Auto-Reload Development
```powershell
# Server automatically reloads on code changes
python -m uvicorn src.main:app --reload
```

### 2. Debug Mode
```powershell
# Already enabled in .env
DEBUG=true
```

### 3. Test Without Starting Server
```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
response = client.get("/health")
print(response.json())
```

### 4. Environment Variables
```powershell
# Check current settings
python -c "from src.config import settings; print(settings.MODEL_NAME)"
```

---

## ⚡ Performance Tips

1. **Use Streaming for Long Responses**
   ```
   POST /api/chat/stream
   ```

2. **Enable Caching** (future enhancement)
   - Redis for session caching
   - Response caching

3. **Parallel Requests**
   - Server handles async requests
   - No blocking I/O

---

## 🎨 Example Requests

### Basic Chat
```json
POST /api/chat
{
  "session_id": 1,
  "message": "Find tourist spots in Seoul"
}
```

### With Trip Context
```json
POST /api/chat
{
  "session_id": 1,
  "trip_id": 123,
  "message": "Show nearby restaurants"
}
```

### Streaming Chat
```json
POST /api/chat/stream
{
  "session_id": 1,
  "message": "Plan a 3-day trip to Busan"
}
```

---

## 🛑 Stop the Server

```powershell
# Press Ctrl+C in terminal

# Or kill process
taskkill /F /PID <PID>

# Docker
docker-compose down
```

---

## ✅ Success Checklist

- [ ] Server starts without errors
- [ ] Health endpoint returns 200
- [ ] API docs accessible at /docs
- [ ] Logs being written to logs/app.log
- [ ] Chat endpoint responds (test with Swagger UI)
- [ ] No import errors in console

---

## 🆘 Need Help?

1. **Check logs first:** `logs/app.log`
2. **Review error messages**
3. **Verify `.env` configuration**
4. **Ensure all packages installed**
5. **Check network connectivity**

---

**Last Updated:** November 22, 2025  
**Status:** ✅ Ready to Run  
**Tested:** ✅ All systems operational

---

## 🎉 You're All Set!

Run the server and start building amazing travel experiences! 🌍✈️🏖️
