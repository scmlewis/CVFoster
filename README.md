# CVFoster 📄

A Streamlit app for CV parsing, job matching, and AI-powered CV optimization.

## Features (Phase 1 MVP)

✅ **CV Parsing**
- Support for PDF, DOCX, and TXT formats
- Automatic section detection (Experience, Education, Skills, etc.)
- OCR fallback for scanned PDFs

✅ **Job Matching**
- Semantic similarity matching using embeddings (Azure OpenAI or TF-IDF)
- Weighted scoring: semantic (50%) + keyword overlap (30%) + seniority level (20%)
- Explainable results with matched CV sections
- Robust error handling with automatic fallback

✅ **CV Rewriting**
- AI-powered text rewriting using Azure OpenAI
- Before/after comparison and download
- Template-based fallback if Azure not available

✅ **Professional UI/UX**
- Custom dark theme with teal/green professional color palette
- Responsive design optimized for all screen sizes
- Smooth animations and transitions (200ms)
- Progress indicators and loading states
- Custom scrollbars and styled components
- Accessibility features (WCAG AA color contrast, keyboard navigation)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. (Optional) Configure Azure OpenAI

The app works with **or without** Azure OpenAI credentials:
- **With Azure**: Uses AI-powered rewriting (recommended)
- **Without Azure**: Uses template-based rewriting (works out of the box)

To enable Azure rewriting:
```bash
# Copy template
cp .env.example .env or Copy-Item .env.example .env (Windows)

# Edit .env with your Azure OpenAI credentials
AZURE_OPENAI_API_KEY=your_key_here
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2025-02-01-preview
AZURE_MODEL=gpt-4o-mini
```

### 3. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 4. Deploy to Streamlit Cloud (Optional)

For production deployment on Streamlit Cloud:

1. **Push code to GitHub** (your repository)
2. **Go to [Streamlit Cloud](https://share.streamlit.io)**
3. **Click "New app"** → Select your repository, branch, and `app.py`
4. **Add Secrets** (Settings → Secrets tab):
   ```toml
   AZURE_OPENAI_API_KEY = "your-key-here"
   AZURE_ENDPOINT = "https://your-resource.openai.azure.com/"
   AZURE_API_VERSION = "2024-02-15-preview"
   AZURE_MODEL = "gpt-4o-mini"
   SKIP_LLM_INIT = false
   ```

### 5. Usage

1. **Upload & Parse**: Go to "Upload & Parse" and upload your CV (PDF, DOCX, or TXT)
2. **Job Matching**: Find relevant job postings based on your CV
3. **Rewrite**: Optimize CV sections with AI (requires Azure credentials for best results)

## Project Structure

```
CVFoster/
├── app.py                           # Main Streamlit entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── PLAN.md                          # Project plan and specifications
│
├── .streamlit/
│   ├── config.toml                  # Streamlit theme configuration (dark mode)
│   └── secrets.toml                 # Secrets template (NOT committed to GitHub)
│
├── src/
│   ├── parse.py                     # CV parsing (PDF/DOCX/TXT)
│   ├── preprocess.py                # Text cleaning and chunking
│   ├── embed_idx.py                 # Embeddings and FAISS indexing
│   ├── matching.py                  # Job matching with scoring
│   ├── llm.py                       # CV rewriting with Azure OpenAI
│   ├── ui_helpers.py                # Streamlit UI components with styling
│   ├── theme.css                    # Dark theme CSS (teal/green palette)
│   ├── css_injection.py             # CSS injection utility
│   └── database.py                  # Database operations
│
└── data/
    ├── jobs/
    │   └── sample_jobs.json         # Sample job postings for testing
    └── samples/                     # Directory for sample CVs
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Parsing** | python-docx, PyMuPDF, Tesseract |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Vector DB** | FAISS (local) |
| **LLM** | DistilBART (seq2seq) |
| **UI Framework** | Streamlit |
| **NLP** | spaCy, scikit-learn |

## Performance Targets (Phase 1)

| Operation | Target |
|-----------|--------|
| CV Parsing (3-page PDF) | ≤ 2s |
| Job Matching (10 jobs) | ≤ 2s |
| CV Rewriting (section) | ≤ 5s |
| Memory per Session | ≤ 2GB |

## Verification Checklist

- [ ] Upload 3 sample CVs (PDF, DOCX, TXT) and verify section detection
- [ ] Load 10 sample job postings and match against each CV (check Precision@3 ≥ 0.7)
- [ ] Generate rewrites for 3 sections and verify output quality
- [ ] Test error handling (unsupported format, corrupted file, empty CV)
- [ ] Verify download functionality for rewritten sections

## Privacy & Security

✅ **All data stays local** — No cloud uploads or external API calls  
✅ **No authentication required** — Standalone desktop app  
✅ **Clear session on restart** — No persistent storage (Phase 1)  
✅ **Open-source** — Full transparency on code and processing

## Roadmap (Phase 2)

- [ ] LinkedIn profile matching
- [ ] Multi-variant rewrites (ATS, Recruiter, Concise)
- [ ] CV versioning and history
- [ ] Data encryption at rest (AES-256)
- [ ] 30-day auto-delete policy
- [ ] Audit logs for data access
- [ ] Advanced privacy controls

## Troubleshooting

### Issue: PDF parsing fails
**Solution**: Ensure Tesseract is installed. For Windows, download from [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).

### Issue: Embeddings take too long
**Solution**: This is expected on CPU. For faster embeddings, use `sentence-transformers/all-MiniLM-L6-v2` with ONNX support or consider GPU acceleration.

### Issue: Spacy model not found
**Solution**: 
```bash
python -m spacy download en_core_web_sm
```

### Issue: DistilBART model too large
**Solution**: You can skip rewriting in Phase 1 by setting `SKIP_LLM=true` in environment.

## Contributing

This is a personal project, but feel free to fork and extend. Key areas for contribution:
- Parsing improvements for edge cases
- Better chunking strategies
- Alternative embedding models
- UI/UX enhancements

## License

MIT License — Use freely for personal and commercial purposes.

## Contact

Questions? File an issue or reach out directly.

---

**Version**: 0.1.0 (MVP Phase 1)  
**Status**: Active Development  
**Last Updated**: March 2026
