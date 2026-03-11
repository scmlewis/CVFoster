# CVFoster 📄

A Streamlit app for CV parsing, job matching, and AI-powered CV optimization.

## Features (Phase 1 MVP)

✅ **CV Parsing**
- Support for PDF, DOCX, and TXT formats
- Automatic section detection (Experience, Education, Skills, etc.)
- OCR fallback for scanned PDFs

✅ **Job Matching**
- Semantic similarity matching using embeddings
- Weighted scoring: semantic (50%) + keyword overlap (30%) + seniority level (20%)
- Explainable results with matched CV sections

✅ **CV Rewriting**
- AI-powered text rewriting using DistilBART
- Concise mode for Phase 1 MVP
- Before/after comparison and download

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 3. Usage

1. **Upload & Parse**: Go to "Upload & Parse" page and upload your CV
2. **Job Matching**: Select a CV section and find matching job postings
3. **Rewrite**: Pick a section to optimize with AI

## Project Structure

```
CVFoster/
├── app.py                           # Main Streamlit entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── PLAN.md                          # Project plan and specifications
│
├── src/
│   ├── parse.py                     # CV parsing (PDF/DOCX/TXT)
│   ├── preprocess.py                # Text cleaning and chunking
│   ├── embed_idx.py                 # Embeddings and FAISS indexing
│   ├── matching.py                  # Job matching with scoring
│   ├── llm.py                       # CV rewriting with DistilBART
│   └── ui_helpers.py                # Streamlit UI components
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
