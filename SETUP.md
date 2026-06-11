# IntelliMatch Chatbot - Setup & Running Guide

## Prerequisites
- Python 3.10+
- pip package manager

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using PowerShell (Recommended)
```powershell
.\run_all.ps1
```

### Option 2: Using Batch File (Windows CMD)
```cmd
run_all.bat
```

### Option 3: Manual Startup

**Terminal 1 - Start API Server:**
```bash
uvicorn app:app --reload --port 8002 --host 0.0.0.0
```

**Terminal 2 - Start Streamlit UI:**
```bash
set STREAMLIT_CONFIG_DIR=%cd%\.streamlit
streamlit run streamlit_app.py
```

## Accessing the Application

- **Streamlit UI:** http://localhost:8501
- **API Health Check:** http://localhost:8002/health
- **API Chat Endpoint:** http://localhost:8002/chat (POST)

## First Run

On first run, the application will:
1. Download the SentenceTransformer model (~82MB) from HuggingFace
2. Cache it in `.model_cache` directory for future use
3. This happens automatically on startup

**Ensure you have internet connection for the first run!**

## Testing the API

Use the included test script:
```bash
python test_manual_chat.py --query "Need someone with Workfront Core and Planning who is available"
```

Or with HTTP payload:
```bash
python test_manual_chat.py --query "Need Fusion expert" --send-http-data
```

## Troubleshooting

### Port Already in Use
- Change port in `run_all.ps1` or `run_all.bat`
- Or kill existing process: `netstat -ano | findstr :8002`

### Model Download Fails
- Check internet connection
- Try manually: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"`

### Streamlit Permission Errors
- Fixed by `.streamlit/config.toml` in project directory
- No need for system-wide permissions

## Data Files

- `data/sample_skill_matrix.json` - Employee skills data
- `data/availability.json` - Employee availability data

Load your own data:
- Via Streamlit UI checkbox "Use local data folder files"
- Via API by posting JSON payloads (see `models.py`)
