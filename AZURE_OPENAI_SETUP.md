# Azure OpenAI Integration Guide

## Overview

CVFoster now supports **Azure OpenAI** for intelligent CV rewriting. The application uses Azure OpenAI GPT-4o-mini as the primary LLM with automatic fallback to template-based rewriting if Azure is unavailable.

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Azure OpenAI account with API credentials
- `.env` file with credentials (see below)

### 2. Configure Azure Credentials

1. **Create a `.env` file** in the project root:
   ```
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_API_VERSION=2025-02-01-preview
   AZURE_MODEL=gpt-4o-mini
   SKIP_LLM_INIT=false
   ```

2. **Get your credentials from Azure:**
   - API Key: Found in Azure Portal > Your Resource > Keys and Endpoint
   - Endpoint: Found in Azure Portal > Your Resource > Keys and Endpoint
   - API Version: Standard API version (listed above is recommended)
   - Model: Your deployed model name (e.g., `gpt-4o-mini`)

3. **Protect your credentials:**
   - `.env` file is **NOT** committed to git (in `.gitignore`)
   - Never hardcode API keys in source code
   - Rotate API keys regularly

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install openai>=1.3.0  # Or already in requirements.txt
```

### 4. Verify Configuration

Run the test script to validate Azure OpenAI setup:

```bash
python test_azure_integration.py
```

Expected output:
```
✓ Azure OpenAI client library is installed
✓ Azure client initialized successfully with credentials from .env
✓ Template-based rewriting works
✓ Azure OpenAI rewriting works!
✓ Multiple section rewriting works!
✓ ALL TESTS PASSED
```

## Features

### Rewriting Modes

CVRewriter now supports three rewriting modes:

1. **Concise Mode**
   - Makes CV sections more concise
   - Removes redundant words while preserving key information
   - Best for: LinkedIn profiles, cover letters

2. **ATS Mode** (Applicant Tracking System)
   - Optimizes for ATS systems
   - Uses standard keywords, avoids special characters
   - Best for: Job applications, online forms

3. **Recruiter Mode**
   - Appeals to human recruiters
   - Uses strong action verbs, highlights metrics
   - Best for: Professional impact, achievements

### Usage in Code

```python
from src.llm import CVRewriter

# Rewrite with Azure OpenAI (primary) or fallback to template
result = CVRewriter.rewrite_section(
    text="Your CV section here",
    mode='recruiter',
    use_azure=True  # Try Azure first, fall back to template
)

if result['success']:
    print(f"Original: {result['original']}")
    print(f"Rewritten: {result['rewritten']}")
    print(f"Method used: {result['method']}")  # 'azure_openai' or 'template_based'
else:
    print(f"Error: {result['error']}")
```

### Using in Streamlit App

The Streamlit app automatically uses Azure OpenAI when available:

1. Start the app: `streamlit run app.py`
2. Navigate to "Rewrite" page
3. Upload a CV and select rewriting mode
4. Click "Rewrite CV"
5. App automatically uses Azure OpenAI if credentials are configured

## Fallback Behavior

If Azure OpenAI is unavailable:
- App automatically falls back to **template-based rewriting**
- Template-based uses regex rules and action verb replacement
- No external API calls, fully offline
- Same rewriting modes (concise, ats, recruiter) supported

## Troubleshooting

### Error: "Azure credentials not configured"
**Solution:** Ensure `.env` file exists in project root with all required fields

### Error: "Azure OpenAI client not installed"
**Solution:** Run `pip install openai>=1.3.0`

### Error: "Invalid API key"
**Solution:** 
- Verify API key in Azure Portal
- Check for extra spaces in `.env` file
- Ensure `.env` file is in correct location (project root)

### App still uses template-based rewriting instead of Azure
**Solution:**
- Verify `.env` file has all required variables
- Run `test_azure_integration.py` to diagnose
- Check logs for specific errors

## Performance

- **Azure OpenAI**: ~2-3 seconds per CV section
- **Template-based**: ~100ms per CV section (instant)
- App uses whichever is available; no degraded UX

## Cost Information

Azure OpenAI API calls incur costs. Recommended for:
- Production deployments
- High-quality rewrites required
- Automated CV processing pipelines

Template-based rewriting is free and sufficient for MVP/testing.

## Security

- API keys stored in `.env` (git-ignored)
- No keys logged or exposed
- Minimal data sent to Azure (just CV text)
- Regular Azure Security updates

## Future Enhancements

- [ ] Multi-variant rewrite generation
- [ ] A/B testing for rewrite effectiveness
- [ ] Custom prompt templates
- [ ] Batch processing with queue
- [ ] Caching of frequently rewritten sections

## Support

For issues or questions:
1. Check logs: `tail logs/*.log`
2. Run `test_azure_integration.py`
3. Verify `.env` configuration
4. Check Azure Portal status
