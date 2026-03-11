"""
Embedding module using Azure OpenAI API.
Lightweight alternative to sentence-transformers - works on Streamlit Cloud.
"""

import logging
import numpy as np
from typing import List, Dict, Optional
from openai import AzureOpenAI
import os

logger = logging.getLogger(__name__)


class AzureEmbeddingIndex:
    """Handler for embeddings using Azure OpenAI API."""

    def __init__(self):
        """Initialize Azure OpenAI client for embeddings."""
        self.client = None
        self.available = False
        self.embedding_dim = 1536  # text-embedding-3-small dimension
        
        try:
            # Get credentials from environment
            api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            azure_endpoint = os.getenv("AZURE_ENDPOINT")
            api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
            
            if not api_key or not azure_endpoint:
                logger.warning("Azure OpenAI credentials not configured")
                return
            
            self.client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version
            )
            self.available = True
            logger.info("Azure OpenAI embedding index initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Azure embeddings: {str(e)}")

    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for a single text using Azure OpenAI API.
        
        Args:
            text: Text string to embed
        
        Returns:
            Embedding array (1536,) or None if failed
        """
        if not self.available or not self.client:
            return None
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return None

    def embed_texts(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        Generate embeddings for multiple texts using Azure OpenAI API.
        
        Args:
            texts: List of text strings
        
        Returns:
            Array of embeddings (N, 1536) or None if failed
        """
        if not self.available or not self.client:
            return None
        
        try:
            response = self.client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            
            embeddings = np.array([item.embedding for item in response.data], dtype=np.float32)
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            return None

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score 0-1, or 0 if failed
        """
        if not self.available:
            return 0.0
        
        emb1 = self.embed_text(text1)
        emb2 = self.embed_text(text2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Cosine similarity
        norm1 = emb1 / (np.linalg.norm(emb1) + 1e-8)
        norm2 = emb2 / (np.linalg.norm(emb2) + 1e-8)
        
        similarity = float(np.dot(norm1, norm2))
        return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]

    def search_similar(
        self,
        query: str,
        stored_embeddings: np.ndarray,
        stored_texts: List[Dict],
        k: int = 5
    ) -> List[Dict]:
        """
        Find most similar texts to query using cosine similarity.
        
        Args:
            query: Query text
            stored_embeddings: Array of stored embeddings (N, 1536)
            stored_texts: List of metadata dicts for each embedding
            k: Number of results to return
        
        Returns:
            List of top-k results with scores
        """
        if not self.available or stored_embeddings is None or len(stored_embeddings) == 0:
            return []
        
        # Get query embedding
        query_emb = self.embed_text(query)
        if query_emb is None:
            return []
        
        # Compute cosine similarity
        query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-8)
        stored_norm = stored_embeddings / (np.linalg.norm(stored_embeddings, axis=1, keepdims=True) + 1e-8)
        
        scores = np.dot(stored_norm, query_norm)
        
        # Get top-k indices
        top_k_indices = np.argsort(scores)[-k:][::-1]
        
        # Return results
        results = []
        for idx in top_k_indices:
            score = float(scores[idx])
            if score > 0:
                result = stored_texts[idx].copy()
                result['similarity_score'] = score
                results.append(result)
        
        return results


class TFIDFEmbedding:
    """Lightweight TF-IDF based matching (fallback when Azure not available)."""
    
    def __init__(self):
        """Initialize TF-IDF matcher."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.stored_texts = []
        self.tfidf_matrix = None
        self.available = True
    
    def fit_and_store(self, texts: List[Dict]):
        """
        Fit TF-IDF on texts and store them.
        
        Args:
            texts: List of dicts with 'text' key
        """
        text_list = [t.get('text', '') for t in texts]
        self.stored_texts = texts
        self.tfidf_matrix = self.vectorizer.fit_transform(text_list)
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict]:
        """
        Find similar texts using TF-IDF.
        
        Args:
            query: Query text
            k: Number of results
        
        Returns:
            List of top-k results
        """
        if self.tfidf_matrix is None:
            return []
        
        query_vec = self.vectorizer.transform([query])
        scores = (self.tfidf_matrix * query_vec.T).toarray().flatten()
        
        top_k_indices = np.argsort(scores)[-k:][::-1]
        
        results = []
        for idx in top_k_indices:
            score = float(scores[idx])
            if score > 0:
                result = self.stored_texts[idx].copy()
                result['similarity_score'] = score
                results.append(result)
        
        return results


# Cache the Azure embedding index - critical for Streamlit Cloud performance
try:
    import streamlit as st
    @st.cache_resource
    def get_azure_embedding_index() -> AzureEmbeddingIndex:
        """Get cached Azure embedding index instance."""
        logger.info("Creating cached Azure embedding index")
        return AzureEmbeddingIndex()
except ImportError:
    # Fallback for non-Streamlit contexts
    def get_azure_embedding_index() -> AzureEmbeddingIndex:
        """Get Azure embedding index instance (non-cached fallback)."""
        return AzureEmbeddingIndex()

