# SYNAPSE-FI Full System Simulation Launcher
# Runs BRIDGE Hub + Entity A + Entity B together

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "SYNAPSE-FI Full System Simulation" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Check if Hub is running
Write-Host "Checking BRIDGE Hub status..." -ForegroundColor Yellow
$hubRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ BRIDGE Hub is running" -ForegroundColor Green
        $hubRunning = $true
    }
} catch {
    Write-Host "❌ BRIDGE Hub is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Starting BRIDGE Hub in background..." -ForegroundColor Yellow
    
    # Start hub in new terminal
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Starting BRIDGE Hub...' -ForegroundColor Cyan; python -m bridge_hub.main"
    
    Write-Host "Waiting for Hub to initialize (10 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check again
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ BRIDGE Hub started successfully" -ForegroundColor Green
            $hubRunning = $true
        }
    } catch {
        Write-Host "⚠️  Warning: Hub may not be fully ready, continuing anyway..." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "Starting Multi-Entity Simulation" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""
Write-Host "🔵 Entity A: Processing transactions at 1.5s interval" -ForegroundColor Blue
Write-Host "🟦 Entity B: Processing transactions at 2.0s interval" -ForegroundColor Blue
Write-Host "📊 Hub Monitor: Displaying stats every 15 seconds" -ForegroundColor Blue
Write-Host ""
Write-Host "Duration: 60 seconds (or press Ctrl+C to stop)" -ForegroundColor Yellow
Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Run simulation
python run_simulation.py 60

Write-Host ""
Write-Host "="*80 -ForegroundColor Green
Write-Host "Simulation Complete!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Green
Write-Host ""
Write-Host "Check the BRIDGE Hub dashboard at http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
