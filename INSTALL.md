# CVFoster Phase 1 MVP - Installation & Quick Start Guide

## 📋 What's Included

The Phase 1 MVP build includes all core modules for:
- ✅ CV Parsing (PDF/DOCX/TXT)
- ✅ Job Matching (with weighted scoring)
- ✅ CV Rewriting (DistilBART-based)
- ✅ Streamlit UI (4 pages: Upload, Matching, Rewrite, About)

## 🚀 Quick Start (Windows)

### Step 1: Install Dependencies

Open PowerShell in the CVFoster directory and run:

```powershell
# Option A: Run the auto setup script
.\setup.bat

# Option B: Manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Validate Installation

```powershell
python validate.py
```

Expected output:
```
✅ All checks passed! Ready to run CVFoster.
```

### Step 3: Run the App

```powershell
streamlit run app.py
```

The app opens automatically at: `http://localhost:8501`

### (Optional) Step 4: Configure Azure OpenAI

For AI-powered CV rewriting (optional - template-based fallback is available):

1. Copy the `.env.example` file to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_API_VERSION=2025-02-01-preview
   AZURE_MODEL=gpt-4o-mini
   SKIP_LLM_INIT=false
   ```

3. Get your credentials from [Azure Portal](https://portal.azure.com#@hotmail.com/resource/subscriptions)

4. **Note:** The `.env` file is automatically excluded from git (see `.gitignore`)

---

## 🐧 Quick Start (Linux/Mac)

### Step 1: Install Dependencies

```bash
# Option A: Run auto setup
bash setup.sh

# Option B: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Validate Installation

```bash
python validate.py
```

### Step 3: Run the App

```bash
streamlit run app.py
```

The app opens automatically at: `http://localhost:8501`

### (Optional) Step 4: Configure Azure OpenAI

For AI-powered CV rewriting (optional - template-based fallback is available):

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_API_VERSION=2025-02-01-preview
   AZURE_MODEL=gpt-4o-mini
   SKIP_LLM_INIT=false
   ```

3. Get your credentials from [Azure Portal](https://portal.azure.com)

4. **Note:** The `.env` file is automatically excluded from git (see `.gitignore`)

---

## 📁 Project Structure

```
CVFoster/
├── app.py                          # Main entry point
├── validate.py                     # Dependency validation
├── requirements.txt                # Python dependencies
├── README.md                       # Full documentation
├── PLAN.md                         # Project plan
├── setup.bat / setup.sh            # Auto-setup scripts
│
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
│
├── src/                            # Core modules
│   ├── __init__.py
│   ├── parse.py                    # CV parsing
│   ├── preprocess.py               # Chunking
│   ├── embed_idx.py                # Embeddings + FAISS
│   ├── matching.py                 # Job matching logic
│   ├── llm.py                      # CV rewriting
│   └── ui_helpers.py               # Streamlit components
│
└── data/
    ├── jobs/
    │   └── sample_jobs.json        # Sample jobs for testing
    └── samples/                    # Place your test CVs here
```

---

## 🧪 Testing the App

### Test Workflow 1: Upload & Parse
1. Go to "Upload & Parse" page
2. Upload a CV file (PDF, DOCX, or TXT)
3. Verify sections are detected (Experience, Skills, Education, etc.)
4. ✅ Expected: Parsed text and sections displayed

### Test Workflow 2: Job Matching
1. After parsing, go to "Job Matching" page
2. Select a CV section
3. Click "Find Matching Jobs"
4. ✅ Expected: Top 3 matching jobs with scores displayed

### Test Workflow 3: CV Rewriting
1. Go to "Rewrite" page
2. Select a CV section
3. Click "Generate Rewrite"
4. ✅ Expected: Original vs. rewritten text with download button

### Test Error Handling
1. Try uploading an unsupported file (.xlsx, .doc)
2. ✅ Expected: Graceful error message
3. Try a corrupted PDF
4. ✅ Expected: Error or OCR fallback

---

## ⚙️ Configuration

### Streamlit Settings (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"

[server]
maxUploadSize = 200          # MB
```

### Environment Variables (Optional)
```bash
# Skip LLM (rewriting) if you want faster startup
export SKIP_LLM=false

# Set logging level
export LOG_LEVEL=INFO
```

---

## 📊 Performance Expectations (Phase 1)

| Operation | Time | Hardware |
|-----------|------|----------|
| Parse CV (3-page PDF) | 1-2s | CPU |
| Embed CV chunks | 0.5-1s | CPU |
| Job matching (10 jobs) | 1-2s | CPU |
| CV rewriting (section) | 5-10s | CPU |
| **Total pipeline** | ~15-25s | CPU |

**Note**: First run will be slower due to model downloads. Subsequent runs are faster.

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'spacy'"
**Solution:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Issue: "StreamlitAppException: Failed to load application"
**Solution:**
```bash
# Check for syntax errors
python -m py_compile app.py

# Run validation
python validate.py
```

### Issue: "Tesseract not found" (PDF parsing error)
**Solution (Windows):**
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location (C:\Program Files\Tesseract-OCR)
3. Or set path: `pytesseract.pytesseract.pytesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

### Issue: "CUDA out of memory" (if using GPU)
**Solution:**
- Use CPU only: Change `device=-1` in `src/llm.py`
- Or reduce model size in Phase 2

### Issue: App runs but features don't work
**Solution:**
1. Run validation script: `python validate.py`
2. Check logs in terminal for errors
3. Ensure spacy model is installed: `python -m spacy download en_core_web_sm`

### Issue: Azure OpenAI features not working
**Solution:**
1. The app automatically falls back to template-based rewriting if Azure is unavailable
2. To enable Azure features, configure `.env` file (see Step 4 above)
3. Verify credentials with: `python test_azure_integration.py`
4. Check that `.env` file exists in project root

### Issue: App shows "Template Mode" instead of Azure OpenAI
**Cause:** The `.env` file is missing or credentials are incorrect  
**Solution:**
- Create `.env` file from `.env.example`
- Fill in your Azure credentials
- Restart the app: `streamlit run app.py`
- You'll see "✅ Azure OpenAI: Connected" in the System Status

---

## ☁️ Deploying to Streamlit Cloud

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add CVFoster"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "New app" > Select your GitHub repo
3. Choose: `app.py` as main file
4. Click "Deploy"

### Step 3: Add Secrets for Azure (Optional)

1. In Streamlit Cloud settings, go to **Secrets**
2. Paste your credentials in TOML format:
   ```toml
   AZURE_OPENAI_API_KEY = "your_api_key"
   AZURE_ENDPOINT = "https://your-resource.openai.azure.com/"
   AZURE_API_VERSION = "2025-02-01-preview"
   AZURE_MODEL = "gpt-4o-mini"
   SKIP_LLM_INIT = false
   ```
3. Click "Save"

### Step 4: Monitor Deployment

The app will redeploy automatically. Check logs in Streamlit Cloud UI.

**Notes:**
- First load may take longer (models downloading)
- `.env` file is NOT used on Streamlit Cloud (use Secrets instead)
- Template-based rewriting works without Azure (no secrets needed)

---

## 📚 Next Steps

### Phase 1 Complete, Phase 2 Features Planned:
- [ ] LinkedIn profile matching
- [ ] Multi-variant rewrites (ATS, Recruiter)
- [ ] CV versioning and history
- [ ] Data encryption at rest
- [ ] Advanced privacy controls

### To Add Your Own Features:
1. Modify relevant `src/*.py` module
2. Update UI in `app.py`
3. Test with `streamlit run app.py`
4. Check performance targets

---

## 📖 Documentation

- **Full Guide**: Read [README.md](README.md)
- **Project Plan**: See [PLAN.md](PLAN.md)
- **Module Docs**: Check docstrings in `src/` files
- **Code Examples**: Look at sample usage in `app.py`

---

## 🆘 Need Help?

1. **Check logs**: Run `streamlit run app.py --logger.level=debug`
2. **Run validator**: `python validate.py`
3. **Review errors**: Check the terminal for detailed error messages
4. **Read docs**: See README.md and PLAN.md

---

**You're all set! Happy CV optimizing! 🚀**
