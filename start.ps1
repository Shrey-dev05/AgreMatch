# Quick Launcher for Hackathon Aggregator
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Launching Hackathon Aggregator (Frontend + Backend)  " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Start Backend
Write-Host "`n[1/3] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn main:app --reload --port 8000"

Start-Sleep -Seconds 3

# Open Browser
Write-Host "[2/3] Opening browser at http://localhost:3000/hackathons..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/hackathons"

# Start Frontend
Write-Host "[3/3] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Green
Set-Location "$PSScriptRoot\frontend"
npm.cmd run dev
