"""
Embeddings Module
Uses SentenceTransformers for generating embeddings of Quran text.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for Quran text using SentenceTransformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
                      (default: all-MiniLM-L6-v2 - lightweight and fast)
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info("Embedding model loaded successfully")
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            numpy array of embeddings (shape: [num_texts, embedding_dim])
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        logger.info(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
        
        Returns:
            numpy array of embedding (shape: [embedding_dim])
        """
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        # Generate a dummy embedding to get dimension
        dummy_embedding = self.generate_embedding("test")
        return len(dummy_embedding)

