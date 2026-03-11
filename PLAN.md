# Plan: Streamlit CV Parsing & Job/LinkedIn Matching

**Goal**
Build a Streamlit app that ingests CVs and LinkedIn text, parses and chunks them, indexes embeddings in a local vector store (FAISS/Chroma), and uses lightweight LLMs for summarization and rewrite. The prototype targets an offline, zero-cost stack using `all-MiniLM-L6-v2` + FAISS/Chroma and optionally small seq2seq or quantized local LLMs for generation.

**Scope Definition**
- **MVP (Phase 1)**: Upload CV → Parse → Chunk → Embed → Job Matching with explainability + Basic Rewrite (one mode).
- **Phase 2**: LinkedIn profile matching, multi-variant rewrites (ATS/recruiter/concise), versioning, advanced privacy.
- **Out of Scope (v1)**: Real-time job scraping, recruiter outreach, advanced NLP models (GPT-4, fine-tuned encoders).

---

## Phase 1: MVP (High-Priority)

1. Project scaffold
   - Create project layout and minimal Streamlit app with upload UI and consent checkbox.
   - Files to create: `app.py`, `requirements.txt`, `README.md`, `src/parse.py`, `src/embed_idx.py`, `src/llm.py`, `src/ui_helpers.py`.

2. Parsing + preprocessing
   - Implement parsers for DOCX/PDF/TXT (python-docx, PyMuPDF/pdftotext, Tesseract for OCR).
   - Implement section detection heuristics and optional PII detection/masking (spaCy/Presidio).
   - Output: normalized text + metadata (sections, offsets).

3. Chunking + embeddings
   - Sentence-level chunking with overlap; tag each chunk with metadata.
   - Embed with `sentence-transformers/all-MiniLM-L6-v2` and persist embeddings.
   - Index using FAISS or Chroma; implement save/load.

4. Job dataset ingestion
   - Ingest job postings from user-provided CSV/JSON; normalize fields (title, description, skills required, seniority level).
   - Expected format: `job_id`, `title`, `description`, `company`, `skills`, `seniority`, `location`.
   - Store as structured data alongside embeddings for reranking.

5. Retrieval & matching
   - **Query flow**: Embed job description (or CV section) → retrieve top-k via FAISS (k=10) → rerank using weighted scoring.
   - **Scoring formula**:
     - Semantic similarity: cosine(embedding_jd, embedding_cv_chunk) × 0.5
     - Keyword overlap: `len(skills_in_jd ∩ skills_in_cv) / len(skills_in_jd)` × 0.3
     - Seniority match: 1.0 if cv_level == jd_level, 0.5 if adjacent level, 0.0 otherwise × 0.2
   - Final score: sum of weighted components, return top-3 matches.
   - **Explainability**: Show matched CV chunks, display individual score components (semantic, keyword, seniority), highlight matched skills.

6. LLM summarization & CV optimization [Phase 2 for multi-variant; Phase 1 = basic rewrite only]
   - **Phase 1 MVP**: Single rewriting mode (concise/general purpose).
   - **Phase 2**: Map-reduce summarization and rewriting for ATS/recruiter/concise variants.
   - Model choice: DistilBART (seq2seq, ~306M params) for local rewriting. GPT4All/llama.cpp optional if DistilBART too slow.
   - Input: CV section (200-500 tokens) → Output: rewritten version (same length ±10%).

7. LinkedIn profile matching & mentor suggestions [Phase 2]
   - Accept LinkedIn export or pasted text → run same chunk/embed/retrieve pipeline.
   - Note: Requires user-provided LinkedIn data or pre-built candidate/mentor database (not included in v1).
   - Future: Add filters (industry, seniority, location) and return match score + rationale.

8. UI polish & UX flows [Phase 1: core; Phase 2: enhanced]
   - **Phase 1 pages**: Upload/Parse, Job Matching (with match explorer), Rewrite (single mode).
   - **Phase 2 pages**: Optimize (multi-variant), LinkedIn Matching, History, Settings.
   - **Phase 1 exports**: TXT download for rewritten sections.
   - **Phase 2 exports**: Full DOCX regeneration with versioning.

9. Privacy, retention & auditing [Phase 2; Phase 1 = local-only]
   - **Phase 1**: Store data locally only (no cloud/database); clear session on app restart; deletion button for uploaded files.
   - **Phase 2**: Encrypt embedding indices at rest (AES-256); implement retention policies (30-day auto-delete) and audit logs for deletions.
   - Consent workflows and detailed privacy policies for Phase 2.

10. Verification & evaluation
   - **Unit tests**: PDF/DOCX/TXT parsing with 5 sample files each; chunking logic with overlap validation.
   - **Integration tests**: embed → index → retrieve → rerank pipeline with 3 CV + 10 job samples.
   - **Evaluation set**: Manual review of top-3 matches for 10 CV-job pairs; target Precision@3 ≥ 0.7 (at least 2/3 matches deemed relevant).
   - **Rewrite quality**: BLEU score (target ≥ 0.35) on generated rewrites vs. 2 human references; manual readability check.
   - **Performance**: Embedding + retrieval ≤ 2s for 100 CV chunks; rewrite generation ≤ 5s per section.

---

## Recommended components (offline/no-cost)

- Parsing: `python-docx`, `PyMuPDF`/`pdftotext`, `tesseract` for OCR.
- NLP: `spaCy` (en_core_web_sm) for NER; `textstat` for readability; `scikit-learn` for TF-IDF keyword extraction.
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (384-dim, ~22MB, optimized for semantic similarity).
  - **Rationale**: Lightweight, fast, and proven on CV/job-matching tasks; alternative: `mpnet-base-v2` (higher quality, slower).
- Vector DB: FAISS (local, no persistence) or Chroma (local with SQLite persistence) for small-scale local apps.
- LLMs for generation: DistilBART (seq2seq, ~306M params) for local rewriting on CPU; optional: `gpt4all` for merges/summarization.
- Session storage: Streamlit `@st.cache_resource` for in-memory index; optional: pickle for persistence across restarts.

---

## File mapping (what to implement where)

- `app.py` — Streamlit entry, multi-page routing (Upload, Job Matching, Rewrite), session state initialization.
- `src/parse.py` — parsing (PDF/DOCX/TXT), OCR fallback, section detection (heuristic: "Experience", "Skills", "Education", etc.).
- `src/preprocess.py` — text cleaning, sentence-level chunking with 50-token overlap, optional PII masking (Phase 2).
- `src/embed_idx.py` — embedding wrapper (sentence-transformers), FAISS index creation/search, in-memory cache.
- `src/matching.py` — job matching with weighted scoring (semantic + keyword + seniority), top-k reranking, score breakdown for explainability.
- `src/llm.py` — DistilBART inference wrapper, prompt templates for rewriting.
- `src/ui_helpers.py` — Streamlit UI components (file uploader, match explorer, score visualizer, download button).
- `data/jobs/sample_jobs.json` — sample job postings for testing (CSV/JSON format).
- `data/samples/` — 3-5 sample CVs (DOCX/PDF/TXT) for manual verification.

---

## Verification checklist (Phase 1 MVP)

1. **Parsing & Upload**
   - Upload 3 sample CVs (1 DOCX, 1 PDF, 1 TXT).
   - Verify parsed text shows correct sections (Experience, Skills, Education, etc.).
   - Check metadata extraction (name, email, phone if present).

2. **Chunking & Embedding**
   - Verify chunks are ~50-100 tokens with 50-token overlap.
   - Confirm all chunks are embedded and stored in FAISS.
   - Check embedding vectors have correct dimensionality (384).

3. **Job Matching**
   - Add 10 sample job postings to index.
   - Run match for each CV; verify top-3 results are manually relevant (Precision@3 ≥ 0.7).
   - Review score breakdown: semantic, keyword, seniority components visible.
   - Check matched chunks are highlighted and traceable to source.

4. **Rewriting**
   - Generate rewrite for 3 CV sections (Experience, Summary, Skills).
   - Verify output is coherent and ≤ 10% length change.
   - Compute BLEU score vs. ground truth (target ≥ 0.35).

5. **Export & Download**
   - Export rewritten section as TXT; verify formatting and content integrity.

6. **Error Handling**
   - Test unsupported file format (XLS); verify graceful error message.
   - Test parsing failure fallback (e.g., corrupted PDF → OCR).
   - Test empty CV; verify no crash.

---

## Decisions & assumptions

- **Offline, zero-cost**: All data stays local; no cloud APIs (trade-off: smaller embedding models).
- **Embedding model**: `all-MiniLM-L6-v2` chosen for speed/size; tested on semantic similarity benchmarks.
  - Alternative: `sentence-transformers/mpnet-base-v2` for higher quality (slower, larger).
- **Data handling**: LinkedIn data is user-provided only; no scraping or API integration in v1.
- **Explainability**: Store chunk → source offsets + original text to highlight matched passages in UI; rerank scores shown as components.
- **Chunking**: Sentence-level (spaCy) with 50-token overlap; assumes well-formatted CVs with clear sections.
- **LLM generation**: DistilBART chosen for balance between quality and speed on CPU; can be upgraded to Flan-T5 if hardware allows.
- **Persistence**: Phase 1 uses in-memory FAISS; Phase 2 adds Chroma with SQLite persistence.
- **Error recovery**: If PDF parsing fails, fallback to OCR (tesseract); if embed fails, skip chunk and log warning.

---

## User Journeys & Workflows

**Journey 1: CV Upload & Job Matching (MVP)**
1. User uploads CV (DOCX/PDF/TXT) via Streamlit file uploader.
2. App parses CV and extracts sections (auto-detect or user-selectable).
3. User loads sample job postings (or uploads custom CSV).
4. App embeds all CV chunks and job descriptions.
5. User selects a CV section or enters a query → app returns top-3 matching jobs.
6. User reviews matches with score breakdown and highlighted text.
7. Optional: User exports top-3 as TXT.

**Journey 2: CV Rewriting (MVP)**
1. User selects a CV section to rewrite.
2. App generates rewritten version using DistilBART (e.g., "Make it more concise").
3. User reviews output and optionally downloads as TXT.
4. Phase 2: User can choose rewrite mode (ATS, recruiter, concise).

---

## Error Handling & Resilience

| Failure Case | Strategy |
|---|---|
| PDF parsing fails | Attempt OCR (tesseract); if OCR fails, return error to user with option to re-upload. |
| Unsupported file format | Graceful error message; list supported formats. |
| Embedding fails | Log error, skip chunk, continue with others; warn user of partial indexing. |
| FAISS search timeout (>2s) | Return partial results if available; suggest user reduce CV size. |
| DistilBART not available | Phase 1: disable rewrite feature with message. Phase 2: fallback to template-based rewrite. |
| Empty or corrupted CSV jobs file | Prompt user to verify format; show sample CSV template. |
| Out of memory (large batch) | Limit session to 5 CVs × 10 jobs; paginate results. |

---

## Performance Targets (Phase 1)

| Operation | Target Latency | Hardware Assumption |
|---|---|---|
| Parse CV (PDF, ~3 pages) | ≤ 2s | CPU + GPU optional |
| Embed CV (10 chunks) | ≤ 1s | CPU |
| Job match + rerank (10 jobs) | ≤ 2s | CPU |
| Rewrite section (DistilBART) | ≤ 5s | CPU; 10s acceptable on slower hardware |
| Full pipeline (upload → match) | ≤ 10s | CPU |
| Memory per session | ≤ 2GB | Single session (FAISS + model cached) |

---

## Next small-step recommendation

Scaffold a minimal runnable prototype (Phase 1 MVP) covering:
1. Upload → parse → chunk → embed → FAISS index.
2. Load sample jobs → rerank by weighted scoring (semantic + keyword + seniority).
3. Streamlit UI: file uploader, parsed text preview, job match results with score breakdown.
4. Simple DistilBART rewrite endpoint.
5. Download rewritten section as TXT.

This fully delivers Phase 1 scope. Phase 2 features (LinkedIn, multi-variant rewrites, encryption, versioning) deferred.
