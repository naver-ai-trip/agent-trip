# Run the AI Travel Agent
# Make sure to activate virtual environment first

Write-Host "Starting AI Travel Planning Agent..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure it." -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Warning: Virtual environment not detected." -ForegroundColor Yellow
    Write-Host "Attempting to activate..." -ForegroundColor Yellow
    
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
    } else {
        Write-Host "Error: Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
        exit 1
    }
}

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Run the application
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Cyan
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
