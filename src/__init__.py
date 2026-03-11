"""
CVFoster: CV Parsing and Job Matching Application
"""

__version__ = "0.1.0"
__author__ = "CVFoster"
__description__ = "AI-powered CV parsing, job matching, and optimization"

from src.parse import CVParser
from src.preprocess import TextPreprocessor
from src.embed_idx import EmbeddingIndex
from src.matching import JobMatcher
from src.llm import CVRewriter

__all__ = [
    'CVParser',
    'TextPreprocessor',
    'EmbeddingIndex',
    'JobMatcher',
    'CVRewriter',
]
