"""
Embedding and indexing module.
Handles sentence embeddings using sentence-transformers and FAISS indexing.
"""

import logging
import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingIndex:
    """Handler for embeddings and vector search."""

    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize embedding model and FAISS index.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Store metadata for each indexed chunk
        self.metadata = []  # List of {text, start_char, end_char, source, chunk_id, etc.}
        self.embeddings = np.empty((0, self.embedding_dim), dtype=np.float32)
        
        logger.info(f"Initialized embedding model: {model_name} (dim={self.embedding_dim})")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
        
        Returns:
            Array of embeddings (N, embedding_dim)
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype(np.float32)

    def add_chunks(
        self,
        chunks: List[Dict],
        source: str,
        metadata_extra: Optional[Dict] = None
    ) -> None:
        """
        Add CV chunks to index.
        
        Args:
            chunks: List of chunk dicts (from preprocess.py)
            source: Source identifier (e.g., filename)
            metadata_extra: Additional metadata to attach
        """
        if not chunks:
            logger.warning(f"No chunks to add from {source}")
            return

        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embed_texts(texts)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store metadata
        for chunk in chunks:
            metadata = {
                'text': chunk['text'],
                'start_char': chunk.get('start_char', 0),
                'end_char': chunk.get('end_char', len(chunk['text'])),
                'chunk_id': chunk.get('chunk_id', len(self.metadata)),
                'source': source,
            }
            if metadata_extra:
                metadata.update(metadata_extra)
            self.metadata.append(metadata)
        
        self.embeddings = np.vstack([self.embeddings, embeddings])
        
        logger.info(f"Added {len(chunks)} chunks from {source}")

    def search(self, query_text: str, k: int = 10) -> List[Dict]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_text: Query text
            k: Number of results to return
        
        Returns:
            List of (metadata, distance) tuples, sorted by similarity
        """
        if len(self.metadata) == 0:
            logger.warning("Index is empty")
            return []

        # Embed query
        query_embedding = self.embed_texts([query_text])[0:1]
        
        # Search
        distances, indices = self.index.search(query_embedding, min(k, len(self.metadata)))
        
        # Collect results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            result = self.metadata[int(idx)].copy()
            # Convert L2 distance to similarity score (lower L2 = higher similarity)
            # Normalize to 0-1 range (rough approximation)
            result['semantic_score'] = max(0, 1 - (distance / 2))
            result['distance'] = float(distance)
            results.append(result)
        
        return results

    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            'total_chunks': len(self.metadata),
            'embedding_dim': self.embedding_dim,
            'model': self.model_name,
            'index_size': len(self.embeddings)
        }

    def clear(self) -> None:
        """Clear index and metadata."""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = []
        self.embeddings = np.empty((0, self.embedding_dim), dtype=np.float32)
        logger.info("Index cleared")


class EmbeddingCache:
    """Simple in-memory cache for embeddings (for session-based use)."""

    def __init__(self):
        """Initialize cache."""
        self._cache = {}

    def get(self, text: str) -> Optional[np.ndarray]:
        """Retrieve cached embedding."""
        return self._cache.get(text)

    def set(self, text: str, embedding: np.ndarray) -> None:
        """Cache an embedding."""
        self._cache[text] = embedding

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()

    def stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'cached_items': len(self._cache),
            'memory_mb': sum(v.nbytes for v in self._cache.values()) / 1024 / 1024
        }
