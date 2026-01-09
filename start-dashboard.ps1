#!/usr/bin/env pwsh
# BRIDGE Hub Dashboard - Quick Start Script
# Launches both the backend API and frontend dashboard

Write-Host "🚀 BRIDGE Hub - Starting Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "📡 Checking BRIDGE Hub backend..." -ForegroundColor Yellow
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Host "✅ Backend is already running on http://localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Backend not detected on http://localhost:8000" -ForegroundColor Red
}

if (-not $backendRunning) {
    Write-Host ""
    Write-Host "Starting BRIDGE Hub backend..." -ForegroundColor Yellow
    Write-Host "Run this in a separate terminal:" -ForegroundColor Cyan
    Write-Host "  cd bridge_hub" -ForegroundColor White
    Write-Host "  uvicorn main:app --reload" -ForegroundColor White
    Write-Host ""
    
    $continue = Read-Host "Press Enter when backend is running (or Ctrl+C to exit)"
}

# Navigate to dashboard directory
Write-Host ""
Write-Host "📦 Starting dashboard..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\dashboard\bridge-insights"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚙️  Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env with default settings" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎨 Launching dashboard on http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard Features:" -ForegroundColor Yellow
Write-Host "  • Overview: Real-time metrics and activity" -ForegroundColor White
Write-Host "  • Patterns: Pattern detection dashboard" -ForegroundColor White
Write-Host "  • Advisories: Advisory management" -ForegroundColor White
Write-Host "  • BRG Graph: Behavioral Risk Graph" -ForegroundColor White
Write-Host "  • Entities: Entity monitoring" -ForegroundColor White
Write-Host "  • Metrics: Performance analytics" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the dashboard" -ForegroundColor Gray
Write-Host ""

# Start the dev server
npm run dev
