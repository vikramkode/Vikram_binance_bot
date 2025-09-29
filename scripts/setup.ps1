$ErrorActionPreference = 'Stop'

Write-Host "== Binance Futures Bot: Setup =="

# Detect Python
$py = "py"
try {
    & $py -3 -c "import sys; print(sys.version)" | Out-Null
} catch {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $py = "python"
    } else {
        Write-Error "Python not found. Install from https://www.python.org/downloads/ or run: winget install -e --id Python.Python.3.12"
        exit 1
    }
}

# Create venv if missing
if (-not (Test-Path .venv)) {
    Write-Host "Creating virtual environment: .venv"
    & $py -3 -m venv .venv
}

$venvPy = Join-Path ".venv" "Scripts/python.exe"
if (-not (Test-Path $venvPy)) {
    $venvPy = Join-Path ".venv" "Scripts/python"
}

Write-Host "Installing requirements..."
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r requirements.txt

# Copy .env if missing
if (-not (Test-Path .env)) {
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Host "Created .env (edit it to add your API keys)"
    }
}

Write-Host "\nSetup complete. Next steps:"
Write-Host "  1) Activate: .\\.venv\\Scripts\\Activate.ps1"
Write-Host "  2) Run a dry-run: python -m src.cli order --type MARKET --side BUY --symbol BTCUSDT --qty 0.001 --testnet --dry-run"
