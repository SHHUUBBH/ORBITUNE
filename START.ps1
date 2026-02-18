# ========================================================
# ORBITUNE - Complete Project Startup Script
# ========================================================
# This script starts the entire ORBITUNE project with one command
# - Backend API (FastAPI with Gemini AI Chatbot)
# - Frontend Dashboard (React/Vite)
# - Automatic dependency installation
# - Health checks
# ========================================================

param(
    [switch]$SkipDependencies,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$ErrorActionPreference = "Continue"

# ========================================================
# Configuration
# ========================================================
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_DIR = Join-Path $SCRIPT_DIR "BACKEND\src"
$FRONTEND_DIR = Join-Path $SCRIPT_DIR "FRONTEND\dashboard\orbitune-sonic-verse-main"
$AI_ML_DIR = Join-Path $SCRIPT_DIR "AI-ML"
$VENV_DIR = Join-Path $AI_ML_DIR "venv"
$ENV_FILE = Join-Path $SCRIPT_DIR ".env"
$REQUIREMENTS = Join-Path $AI_ML_DIR "requirements.txt"

# ========================================================
# Utility Functions
# ========================================================
function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor White
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-CommandExists {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Wait-ForHealthCheck {
    param(
        [string]$Url,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )
    
    Write-Info "Waiting for service to be ready at $Url..."
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "Service is ready!"
                return $true
            }
        } catch {
            # Service not ready yet
        }
        
        Write-Host "." -NoNewline
        Start-Sleep -Seconds $DelaySeconds
    }
    
    Write-Host ""
    Write-Warning "Service did not respond within expected time"
    return $false
}

# ========================================================
# Banner
# ========================================================
Clear-Host
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Magenta
Write-Host "           ORBITUNE - 3D Audio Experience             " -ForegroundColor Magenta
Write-Host "=======================================================" -ForegroundColor Magenta
Write-Host "   Version: 1.0.0" -ForegroundColor Gray
Write-Host "   Project: $SCRIPT_DIR" -ForegroundColor Gray
Write-Host ""

# ========================================================
# Pre-flight Checks
# ========================================================
Write-Header "Pre-flight System Checks"

# Check Python
if (-not (Test-CommandExists "python")) {
    Write-Error-Message "Python is not installed!"
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}
$pythonVersion = python --version 2>&1
Write-Success "Python: $pythonVersion"

# Check Node.js
if (-not (Test-CommandExists "node")) {
    Write-Error-Message "Node.js is not installed!"
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
$nodeVersion = node --version
Write-Success "Node.js: $nodeVersion"

# Check npm
if (-not (Test-CommandExists "npm")) {
    Write-Error-Message "npm is not installed!"
    Write-Host "npm should come with Node.js installation" -ForegroundColor Yellow
    exit 1
}
$npmVersion = npm --version
Write-Success "npm: v$npmVersion"

# Check .env file
if (-not (Test-Path $ENV_FILE)) {
    Write-Error-Message ".env file not found!"
    Write-Host "Creating .env file with placeholder..." -ForegroundColor Yellow
    "GEMINI_API_KEY=AIzaSyDezZ6Egk35D7DUiJEkp9DEjbDhQZCNYwE" | Out-File -FilePath $ENV_FILE -Encoding UTF8
    Write-Success "Created .env file"
} else {
    Write-Success "Environment file found"
}

# Check directories
if (-not (Test-Path $BACKEND_DIR)) {
    Write-Error-Message "Backend directory not found: $BACKEND_DIR"
    exit 1
}
if (-not (Test-Path $FRONTEND_DIR)) {
    Write-Error-Message "Frontend directory not found: $FRONTEND_DIR"
    exit 1
}

Write-Success "All system checks passed!"

# ========================================================
# Backend Setup
# ========================================================
if (-not $FrontendOnly) {
    Write-Header "Setting Up Python Backend"

    # Check/Create Virtual Environment
    if (-not (Test-Path $VENV_DIR)) {
        Write-Info "Creating Python virtual environment..."
        python -m venv $VENV_DIR
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Message "Failed to create virtual environment"
            exit 1
        }
        Write-Success "Virtual environment created"
    } else {
        Write-Success "Virtual environment exists"
    }

    # Activate Virtual Environment
    $ACTIVATE_SCRIPT = Join-Path $VENV_DIR "Scripts\Activate.ps1"
    if (Test-Path $ACTIVATE_SCRIPT) {
        Write-Info "Activating virtual environment..."
        & $ACTIVATE_SCRIPT
        Write-Success "Virtual environment activated"
    }

    # Install/Update Python Dependencies
    if (-not $SkipDependencies) {
        Write-Info "Installing Python dependencies (this may take a few minutes on first run)..."
        $VENV_PYTHON = Join-Path $VENV_DIR "Scripts\python.exe"
        
        if (Test-Path $VENV_PYTHON) {
            & $VENV_PYTHON -m pip install --upgrade pip --quiet
            & $VENV_PYTHON -m pip install -r $REQUIREMENTS --quiet
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Python dependencies installed"
            } else {
                Write-Warning "Some dependencies may have failed to install"
            }
        }
    } else {
        Write-Info "Skipping dependency installation"
    }
}

# ========================================================
# Frontend Setup
# ========================================================
if (-not $BackendOnly) {
    Write-Header "Setting Up React Frontend"

    Push-Location $FRONTEND_DIR

    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Info "Installing Node.js dependencies (this may take a few minutes)..."
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Node.js dependencies installed"
        } else {
            Write-Warning "Some dependencies may have failed to install"
        }
    } elseif (-not $SkipDependencies) {
        Write-Info "Checking for dependency updates..."
        npm install --quiet
        Write-Success "Dependencies up to date"
    } else {
        Write-Success "Node modules exist"
        Write-Info "Skipping dependency installation"
    }

    Pop-Location
}

# ========================================================
# Start Services
# ========================================================
Write-Header "Starting ORBITUNE Services"

# Start Backend
if (-not $FrontendOnly) {
    Write-Info "Starting Backend API Server..."
    Write-Host "   URL: http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "   Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
    Write-Host ""

    $VENV_PYTHON = Join-Path $VENV_DIR "Scripts\python.exe"
    
    # Start backend in a new PowerShell window
    $backendCommand = "Write-Host 'ORBITUNE Backend Server' -ForegroundColor Green; Write-Host '=======================================' -ForegroundColor Green; Write-Host ''; Set-Location '$BACKEND_DIR'; & '$VENV_PYTHON' -m uvicorn app:app --reload --host 127.0.0.1 --port 8000"

    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand
    Write-Success "Backend server started in new window"
    
    # Wait for backend to be ready
    Start-Sleep -Seconds 3
    Wait-ForHealthCheck -Url "http://127.0.0.1:8000/api/chatbot/health" -MaxAttempts 15
}

# Start Frontend
if (-not $BackendOnly) {
    Write-Info "Starting Frontend Development Server..."
    Write-Host "   URL: http://localhost:5173" -ForegroundColor Cyan
    Write-Host "   Dashboard: http://localhost:5173/dashboard" -ForegroundColor Cyan
    Write-Host ""

    # Start frontend in a new PowerShell window
    $frontendCommand = "Write-Host 'ORBITUNE Frontend Dashboard' -ForegroundColor Blue; Write-Host '=======================================' -ForegroundColor Blue; Write-Host ''; Set-Location '$FRONTEND_DIR'; npm run dev"

    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand
    Write-Success "Frontend server started in new window"
    
    # Wait for frontend to be ready
    Start-Sleep -Seconds 5
    Wait-ForHealthCheck -Url "http://localhost:5173" -MaxAttempts 20
}

# ========================================================
# Success Message
# ========================================================
Write-Header "ORBITUNE is Ready!"

Write-Host ""
Write-Host "Your application is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "   Dashboard:     http://localhost:5173/dashboard" -ForegroundColor White
Write-Host "   Backend API:   http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   API Docs:      http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "   Health Check:  http://127.0.0.1:8000/api/chatbot/health" -ForegroundColor White
Write-Host ""
Write-Host "Features Available:" -ForegroundColor Cyan
Write-Host "   [OK] YouTube to 3D Audio Conversion" -ForegroundColor White
Write-Host "   [OK] AI Music Companion (Gemini Flash 2.0)" -ForegroundColor White
Write-Host "   [OK] Tab Key to Switch Search/Chat Modes" -ForegroundColor White
Write-Host "   [OK] Real-time Audio Visualization" -ForegroundColor White
Write-Host "   [OK] Debug Panel (Press Ctrl+Space)" -ForegroundColor White
Write-Host ""
Write-Host "Keyboard Shortcuts:" -ForegroundColor Cyan
Write-Host "   Tab        - Switch between Search and Chat modes" -ForegroundColor White
Write-Host "   Ctrl+Space - Toggle Developer Debug Panel" -ForegroundColor White
Write-Host ""
Write-Host "Quick Start Guide:" -ForegroundColor Cyan
Write-Host "   1. Open dashboard in your browser" -ForegroundColor White
Write-Host "   2. Try Chat Mode: Press Tab -> 'I'm feeling happy!'" -ForegroundColor White
Write-Host "   3. Try Search Mode: Press Tab -> 'Bohemian Rhapsody'" -ForegroundColor White
Write-Host ""
Write-Host "To Stop:" -ForegroundColor Yellow
Write-Host "   Close the Backend and Frontend PowerShell windows" -ForegroundColor White
Write-Host "   or press Ctrl+C in each window" -ForegroundColor White
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "           Enjoy ORBITUNE!                            " -ForegroundColor Magenta
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Open browser automatically
Write-Info "Opening dashboard in your default browser..."
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173/dashboard"

Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
