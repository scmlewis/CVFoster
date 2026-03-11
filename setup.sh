#!/bin/bash
# CVFoster Setup and Run Script

echo "🚀 CVFoster Phase 1 MVP Setup"
echo "=============================="

# Check Python version
echo "Checking Python version..."
python --version

# Create virtual environment (optional)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    
    # Activate venv
    if [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate  # Windows Git Bash
    else
        source venv/bin/activate  # Linux/Mac
    fi
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download spacy model
echo "Downloading spacy language model..."
python -m spacy download en_core_web_sm

# Create sample data directories if missing
mkdir -p data/samples
mkdir -p data/jobs

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the app:"
echo "  streamlit run app.py"
echo ""
echo "Then visit: http://localhost:8501"
