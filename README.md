# IntelliMatch AI Chatbot (Dual Mode: `data/` fallback + HTTP payload)

A chatbot-based resource matching system that intelligently matches project requirements with available team members based on skills and availability.

**Dual Mode Support:**
1. **Manual testing** using files in the `data/` folder
2. **HTTP/Fusion execution** by sending `skill_matrix` and `availability` in the API payload

---

## 📁 Folder Structure

```
intellimatch_chatbot_dual_mode/
├── app.py                          # FastAPI application
├── engine.py                       # Matching logic & semantic search
├── models.py                       # Pydantic request models
├── data_loader.py                  # Data normalization
├── streamlit_app.py                # Web UI
├── test_manual_chat.py             # CLI testing tool
├── requirements.txt                # Python dependencies
├── SETUP.md                        # Detailed setup guide
├── run_all.ps1                     # PowerShell startup script
├── run_all.bat                     # Windows batch startup script
├── .streamlit/config.toml          # Streamlit configuration
├── .model_cache/                   # Cached ML models (auto-created)
└── data/
    ├── sample_skill_matrix.json    # Employee skills data
    └── availability.json           # Employee availability data
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Internet connection (first run only for model download)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run Both Services

**Option A: Using PowerShell (Recommended)**
```powershell
Run the server First
uvicorn app:app --reload --port 8002 
.\run_all.ps1

```

**Option B: Using Windows Command Prompt**
```cmd
run_all.bat
```

**Option C: Manual Setup (Two Separate Terminals)**

Terminal 1 - Start API Server:
```bash
uvicorn app:app --reload --port 8002 --host 0.0.0.0
```

Terminal 2 - Start Streamlit UI:
```bash
$env:STREAMLIT_CONFIG_DIR = "$pwd\.streamlit"
streamlit run streamlit_app.py
```

---

## 🌐 Access the Application

| Service | URL | Purpose |
|---------|-----|---------|
| **Streamlit UI** | http://localhost:8501 | Web interface for candidate matching |
| **API Health** | http://localhost:8002/health | Check API status |
| **API Chat** | http://localhost:8002/chat | POST endpoint for matching requests |

---

## 📋 How to Use

### Using Streamlit Web UI

1. Open **http://localhost:8501** in your browser
2. Enter a project requirement in the search box (e.g., "Need someone with Workfront Core and Planning who is available")
3. Adjust the "Top K" slider (1-10 candidates)
4. Click **"Find Candidates"**
5. View results with match scores and detailed breakdowns

### Using CLI Test Tool

**Test with local data files:**
```bash
python test_manual_chat.py --query "Need someone with Workfront Core who is available"
```

**Test with HTTP payload (like Fusion):**
```bash
python test_manual_chat.py --query "Need Workfront Planning expert" --send-http-data
```

### Using API Directly

**Example POST request to `/chat`:**
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Need someone with Workfront Core and Planning who is available",
    "top_k": 5
  }'
```

**With custom data payload:**
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Need someone with Workfront Core and Planning who is available",
    "skill_matrix": [YOUR_SKILL_MATRIX_JSON],
    "availability": [YOUR_AVAILABILITY_JSON],
    "top_k": 5
  }'
```

---

## 📊 Data Format

### Skill Matrix (sample_skill_matrix.json)
```json
[
  {
    "Name": "John Doe",
    "details": [
      {
        "Core Verdict": "Expert",
        "Normalizing core": 0.95,
        "Planning Verdict": "Intermediate",
        "Normalizing Planning": 0.72,
        "Overall Verdict": "Highly Recommended",
        "Overall Capability Strength": 0.89
      }
    ]
  }
]
```

### Availability (availability.json)
```json
[
  {
    "Resource name": "John Doe",
    "hours": [35, 40, 42, 38, 45]
  }
]
```

---

## 🔧 Troubleshooting

### Port Already in Use
- Change port in startup scripts or use different port
- Find and kill process: `netstat -ano | findstr :8002`

### Model Download Fails (First Run)
- Ensure internet connection is active
- Model (~82MB) will be downloaded from HuggingFace on first run
- Cached in `.model_cache/` for future runs

### Streamlit Permission Errors
- Fixed automatically with `.streamlit/config.toml` in project folder
- Uses local config instead of user profile directory

### API Not Responding
- Verify server is running: `Invoke-RestMethod http://localhost:8002/health`
- Check port 8002 is not blocked by firewall

---

## 🏗️ Architecture

- **Backend:** FastAPI + Uvicorn (async, scalable)
- **NLP:** Sentence-Transformers (semantic matching)
- **Frontend:** Streamlit (interactive web UI)
- **Scoring:** Multi-factor matching (skills + availability + semantic similarity)

---

## 🔄 Data Flow

1. User enters requirement in Streamlit UI or sends API request
2. System extracts required capabilities from query
3. Semantic matching ranks candidates by skill match
4. Availability status applied as multiplier
5. Top K results returned with detailed breakdown

---

## 📝 Notes

- This system preserves existing architecture:
  - FastAPI backend supports HTTP integration with Fusion
  - Manual testing works with local data files
  - Chatbot is an additional input method, not replacement
- All services must run with internet on first startup (model download)
- Configuration files are stored locally in project directory for portability
- Model is cached after first download for offline operation
