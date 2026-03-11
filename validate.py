"""
CVFoster Dependency Validation Script
Checks that all required packages are installed and working.
"""

import sys
import importlib
from typing import List, Tuple

def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Check if a package is installed and importable."""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, f"✅ {package_name:30} {version}"
    except ImportError as e:
        return False, f"❌ {package_name:30} NOT INSTALLED - {str(e)}"

def main():
    """Run all validation checks."""
    
    print("\n" + "="*70)
    print("CVFoster Dependency Validation")
    print("="*70 + "\n")
    
    # List of packages to check
    packages = [
        ('streamlit', 'streamlit'),
        ('python-docx', 'docx'),
        ('PyMuPDF', 'fitz'),
        ('sentence-transformers', 'sentence_transformers'),
        ('faiss-cpu', 'faiss'),
        ('spacy', 'spacy'),
        ('torch', 'torch'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('scikit-learn', 'sklearn'),
        ('transformers', 'transformers'),
    ]
    
    all_ok = True
    results = []
    
    print("Checking installed packages:\n")
    for package_name, import_name in packages:
        ok, message = check_package(package_name, import_name)
        results.append(message)
        if not ok:
            all_ok = False
    
    for result in results:
        print(result)
    
    # Check spacy model
    print("\nChecking spaCy models:\n")
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print(f"✅ {'spacy/en_core_web_sm':30} loaded successfully")
    except Exception as e:
        print(f"❌ {'spacy/en_core_web_sm':30} NOT FOUND - Run: python -m spacy download en_core_web_sm")
        all_ok = False
    
    # Check project structure
    print("\nChecking project structure:\n")
    
    import os
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'src/parse.py',
        'src/preprocess.py',
        'src/embed_idx.py',
        'src/matching.py',
        'src/llm.py',
        'src/ui_helpers.py',
        'data/jobs/sample_jobs.json',
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path:40}")
        else:
            print(f"❌ {file_path:40} MISSING")
            all_ok = False
    
    # Summary
    print("\n" + "="*70)
    if all_ok:
        print("✅ All checks passed! Ready to run CVFoster.")
        print("\nTo start the app, run:")
        print("  streamlit run app.py")
        print("\nThen visit: http://localhost:8501")
    else:
        print("❌ Some checks failed. Please install missing packages:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_sm")
    print("="*70 + "\n")
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
