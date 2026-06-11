# PowerShell script to run both servers
# Set environment variables
$env:STREAMLIT_CONFIG_DIR = "$(Get-Location)\.streamlit"
$env:HF_HOME = "$(Get-Location)\.model_cache"
$env:TRANSFORMERS_CACHE = "$(Get-Location)\.model_cache"

Write-Host "Starting IntelliMatch servers..." -ForegroundColor Green
Write-Host "Config Directory: $($env:STREAMLIT_CONFIG_DIR)" -ForegroundColor Cyan
Write-Host "Model Cache: $($env:HF_HOME)" -ForegroundColor Cyan

# Start Uvicorn in a new window
Write-Host "Starting Uvicorn API server on http://localhost:8002..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "uvicorn app:app --reload --port 8002 --host 0.0.0.0" -WorkingDirectory $(Get-Location)

# Wait for API to start
Start-Sleep -Seconds 3

# Start Streamlit
Write-Host "Starting Streamlit UI on http://localhost:8501..." -ForegroundColor Yellow
streamlit run streamlit_app.py --logger.level=error
