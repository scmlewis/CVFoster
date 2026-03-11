"""
Text preprocessing and chunking module.
Handles text cleaning, sentence segmentation, and chunk creation with overlap.
"""

import logging
import re
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Handler for text cleaning and chunking."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove page markers
        text = text.replace('---', '').replace('Page', '')
        # Remove excessive newlines
        text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
        return text

    @staticmethod
    def segment_sentences(text: str) -> List[str]:
        """
        Segment text into sentences using simple regex (spacy optional).
        
        Args:
            text: Text to segment
        
        Returns:
            List of sentences
        """
        # First try spacy if available
        try:
            import spacy
            nlp = spacy.load('en_core_web_sm')
            doc = nlp(text[:1000000])  # Limit to avoid memory issues
            sentences = [sent.text.strip() for sent in doc.sents]
            if sentences:
                return sentences
        except Exception:
            pass
        
        # Fallback to simple regex-based sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def create_chunks(
        text: str,
        chunk_size: int = 100,
        overlap: int = 50,
        method: str = 'token'
    ) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size (tokens or characters)
            overlap: Overlap size (tokens or characters)
            method: 'token' or 'char'
        
        Returns:
            List of chunk dicts with text, start, end, and metadata
        """
        if method == 'token':
            return TextPreprocessor._chunk_by_token(text, chunk_size, overlap)
        elif method == 'char':
            return TextPreprocessor._chunk_by_char(text, chunk_size, overlap)
        else:
            raise ValueError(f"Unknown chunking method: {method}")

    @staticmethod
    def _chunk_by_token(text: str, chunk_size: int = 100, overlap: int = 50) -> List[Dict]:
        """
        Chunk text by approximate token count.
        Uses word count as proxy (1 word ≈ 1.3 tokens).
        """
        # Simple word-based tokenization
        words = text.split()
        word_chunk_size = int(chunk_size / 1.3)  # Adjust for token-to-word ratio
        word_overlap = int(overlap / 1.3)

        chunks = []
        start_idx = 0

        while start_idx < len(words):
            end_idx = min(start_idx + word_chunk_size, len(words))
            chunk_text = ' '.join(words[start_idx:end_idx])

            # Find char positions in original text
            chunk_start = text.find(chunk_text)
            chunk_end = chunk_start + len(chunk_text)

            chunks.append({
                'text': chunk_text,
                'start_char': chunk_start if chunk_start != -1 else 0,
                'end_char': chunk_end,
                'word_count': len(chunk_text.split()),
                'chunk_id': len(chunks)
            })

            # Move start with overlap
            start_idx += word_chunk_size - word_overlap

        return chunks

    @staticmethod
    def _chunk_by_char(text: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
        """
        Chunk text by character count.
        """
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]

            chunks.append({
                'text': chunk_text,
                'start_char': start,
                'end_char': end,
                'char_count': len(chunk_text),
                'chunk_id': len(chunks)
            })

            # Move start with overlap
            start += chunk_size - overlap

        return chunks

    @staticmethod
    def preprocess_cv(raw_text: str, chunk_size: int = 100, chunk_overlap: int = 50) -> Dict:
        """
        Complete preprocessing pipeline for CV text.
        
        Args:
            raw_text: Raw parsed CV text
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap in tokens
        
        Returns:
            Dict with cleaned text and chunks
        """
        # Clean text
        cleaned = TextPreprocessor.clean_text(raw_text)

        # Create chunks
        chunks = TextPreprocessor.create_chunks(
            cleaned,
            chunk_size=chunk_size,
            overlap=chunk_overlap,
            method='token'
        )

        return {
            'original_text': raw_text,
            'cleaned_text': cleaned,
            'chunks': chunks,
            'total_chunks': len(chunks),
            'char_count': len(cleaned)
        }

    @staticmethod
    def preprocess_job_description(raw_text: str) -> Dict:
        """
        Preprocessing for job descriptions (typically shorter than CVs).
        
        Args:
            raw_text: Raw job description text
        
        Returns:
            Dict with cleaned text and chunks
        """
        cleaned = TextPreprocessor.clean_text(raw_text)
        chunks = TextPreprocessor.create_chunks(
            cleaned,
            chunk_size=150,  # Slightly larger for job descriptions
            overlap=50,
            method='token'
        )

        return {
            'original_text': raw_text,
            'cleaned_text': cleaned,
            'chunks': chunks,
            'total_chunks': len(chunks),
            'char_count': len(cleaned)
        }
