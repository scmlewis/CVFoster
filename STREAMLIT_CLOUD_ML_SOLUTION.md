# Job Matching on Streamlit Cloud - Solution Guide

## Problem
The Job Matching feature requires `sentence-transformers`, `torch`, and `faiss` - heavy ML libraries that won't install on Streamlit Cloud.

## Solution
Use **Azure OpenAI Embeddings** instead of local ML libraries. You already have Azure OpenAI configured, so this integrates seamlessly.

### Benefits
✅ **No heavy ML libraries** - Works on Streamlit Cloud free tier  
✅ **Leverages existing Azure setup** - Uses your Azure OpenAI API key  
✅ **Better quality** - Azure's embeddings are production-grade  
✅ **Scalable** - Cloud-based, handles large documents easily  
✅ **Fallback to TF-IDF** - Uses scikit-learn (already installed) if Azure unavailable  

## Implementation Steps

### 1. New module created: `src/embedding_azure.py`
This provides two classes:
- `AzureEmbeddingIndex`: Uses Azure OpenAI for sentence embeddings
- `TFIDFEmbedding`: Lightweight TF-IDF fallback (already have scikit-learn)

### 2. Update Job Matching in `app.py` (lines 327-380)

Replace the embedding index check with:

```python
def page_job_matching():
    """Job Matching page."""
    render_page_header(
        "Job Matching",
        "Find job positions that match your CV",
        emoji="🎯",
        style="green",
    )
    
    # Try Azure embeddings first, fall back to TF-IDF
    from src.embedding_azure import AzureEmbeddingIndex, TFIDFEmbedding
    
    embedding_index = AzureEmbeddingIndex()
    if not embedding_index.available:
        # Fall back to TF-IDF
        embedding_index = TFIDFEmbedding()
        st.info("💡 Using lightweight TF-IDF matching (Azure OpenAI not configured)")
    else:
        st.info("✅ Using Azure OpenAI embeddings for semantic matching")
    
    if st.session_state.state.cv_text is None:
        st.warning("Please upload and parse a CV first on the Upload & Parse page.")
        return
    
    # Load jobs...
    # (rest of existing code)
```

### 3. Adapt Job Matching Logic

The existing `JobMatcher` class in `src/matching.py` already handles:
- Keyword extraction (skills, seniority level)
- Scoring and ranking
- Explainable results

You just need to integrate the new embeddings:

```python
# In your matching function:
if isinstance(embedding_index, AzureEmbeddingIndex):
    # Use semantic matching with embeddings
    similar_jobs = embedding_index.search_similar(
        cv_chunk_summary,
        job_embeddings,
        job_metadata,
        k=5
    )
else:
    # Use TF-IDF matching
    similar_jobs = embedding_index.search_similar(
        cv_chunk_summary,
        k=5
    )

# Combine with JobMatcher.calculate_keyword_score()
```

## API Costs

Azure OpenAI embeddings are **very inexpensive**:
- **text-embedding-3-small**: $0.02 per 1M tokens
- Typical CV + job description: 500-1000 tokens per match
- ~$0.00001 per job match

## Fallback Strategy

```
Priority:
1. Azure OpenAI Embeddings (best quality, requires credentials)
   ↓
2. TF-IDF (always available, uses scikit-learn)
   ↓
3. Keyword matching only (simple overlap scoring)
```

## Testing Locally

Before deploying, test locally:

```bash
# Install optional dependency for testing (not needed on cloud)
pip install openai

# Run the app
streamlit run app.py
```

The app will auto-detect Azure credentials from `.env` and use embeddings.

## What This Means for Users

**On Streamlit Cloud:**
- Job Matching feature **now works**
- Uses semantic similarity (Azure OpenAI)
- Same quality as local version
- No degraded functionality

**Local development:**
- Can still use sentence-transformers if installed
- Falls back to Azure embeddings if not
- Falls back to TF-IDF if Azure not configured

## Questions?

- Does your `.env` have `AZURE_OPENAI_API_KEY` and `AZURE_ENDPOINT` set?
- Want to implement this now or test the TF-IDF fallback first?
- Need help integrating with your existing matching logic?
