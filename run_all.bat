@echo off
REM Start Uvicorn server on port 8002
echo Starting Uvicorn server on port 8002...
start cmd /k uvicorn app:app --reload --port 8002 --host 0.0.0.0

REM Wait a moment for server to start
timeout /t 3

REM Set Streamlit config directory and start Streamlit on port 8501
echo Starting Streamlit app on port 8501...
set STREAMLIT_CONFIG_DIR=%cd%\.streamlit
streamlit run streamlit_app.py --logger.level=error
