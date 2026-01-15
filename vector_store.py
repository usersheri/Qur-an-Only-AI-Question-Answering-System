"""
Vector Store Module
Uses FAISS for efficient similarity search over Quran embeddings.
"""

import faiss
import numpy as np
from typing import List, Tuple
import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for Quran embeddings."""
    
    def __init__(self, embedding_dim: int):
        """
        Initialize the vector store.
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatIP(embedding_dim)  # Inner product for similarity
        self.ayah_ids: List[str] = []
        logger.info(f"Initialized FAISS index with dimension {embedding_dim}")
    
    def add_embeddings(self, embeddings: np.ndarray, ayah_ids: List[str]):
        """
        Add embeddings to the index.
        
        Args:
            embeddings: numpy array of embeddings (shape: [num_ayahs, embedding_dim])
            ayah_ids: List of ayah IDs corresponding to embeddings
        """
        if len(embeddings) != len(ayah_ids):
            raise ValueError(f"Mismatch: {len(embeddings)} embeddings but {len(ayah_ids)} IDs")
        
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {embeddings.shape[1]}")
        
        # Convert to float32 for FAISS
        embeddings = embeddings.astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        self.ayah_ids.extend(ayah_ids)
        
        logger.info(f"Added {len(embeddings)} embeddings to vector store")
        logger.info(f"Total vectors in index: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar ayahs.
        
        Args:
            query_embedding: Query embedding vector (shape: [embedding_dim])
            k: Number of results to return
        
        Returns:
            List of tuples (ayah_id, distance) sorted by similarity (lowest distance first)
        """
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        query_embedding = query_embedding.astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.ayah_ids):
                results.append((self.ayah_ids[idx], float(dist)))
        
        return results
    
    def save(self, filepath: str):
        """Save the vector store to disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(path))
        
        # Save ayah IDs
        ids_path = path.with_suffix('.ids.pkl')
        with open(ids_path, 'wb') as f:
            pickle.dump(self.ayah_ids, f)
        
        logger.info(f"Saved vector store to {filepath}")
    
    def load(self, filepath: str):
        """Load the vector store from disk."""
        path = Path(filepath)
        
        # Load FAISS index
        self.index = faiss.read_index(str(path))
        self.embedding_dim = self.index.d
        
        # Load ayah IDs
        ids_path = path.with_suffix('.ids.pkl')
        with open(ids_path, 'rb') as f:
            self.ayah_ids = pickle.load(f)
        
        logger.info(f"Loaded vector store from {filepath}")
        logger.info(f"Total vectors: {self.index.ntotal}")

