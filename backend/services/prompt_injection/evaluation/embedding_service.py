"""
Embedding service for semantic similarity analysis.

This service provides embeddings using either OpenAI API or local sentence-transformers.
Supports caching for performance optimization.
"""
import os
from typing import List, Optional, Dict
from functools import lru_cache
import numpy as np

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class EmbeddingService:
    """
    Service for generating text embeddings.
    
    Supports both OpenAI embeddings (paid, high quality) and
    sentence-transformers (free, local, fast).
    """
    
    def __init__(
        self,
        use_openai: bool = False,
        openai_api_key: Optional[str] = None,
        openai_model: str = "text-embedding-3-small",
        local_model: str = "all-MiniLM-L6-v2",
        cache_size: int = 128
    ):
        """
        Initialize embedding service.
        
        Args:
            use_openai: Whether to use OpenAI embeddings (default: False, uses local)
            openai_api_key: OpenAI API key (required if use_openai=True)
            openai_model: OpenAI embedding model name
            local_model: Local sentence-transformers model name
            cache_size: LRU cache size for embeddings
        """
        self.use_openai = use_openai
        self.cache: Dict[str, List[float]] = {}
        
        if use_openai:
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "openai package required for OpenAI embeddings. "
                    "Install with: pip install openai"
                )
            if not openai_api_key:
                raise ValueError("openai_api_key required when use_openai=True")
            
            self.client = AsyncOpenAI(api_key=openai_api_key)
            self.model = openai_model
            self._embed_func = self._get_openai_embedding
        else:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "sentence-transformers required for local embeddings. "
                    "Install with: pip install sentence-transformers"
                )
            
            # Load model (this is synchronous, done once)
            self.model = SentenceTransformer(local_model)
            self._embed_func = self._get_local_embedding
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text string.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        # Check cache first
        text_key = text[:100]  # Use first 100 chars as cache key
        if text_key in self.cache:
            return self.cache[text_key]
        
        # Generate embedding
        embedding = await self._embed_func(text)
        
        # Cache it
        if len(self.cache) < 128:  # Simple cache limit
            self.cache[text_key] = embedding
        
        return embedding
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts (more efficient).
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        import asyncio
        
        if self.use_openai:
            # OpenAI batch API
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        else:
            # Local batch processing
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(texts, convert_to_numpy=False)
            )
            
            # Handle tensor conversion
            if TORCH_AVAILABLE and isinstance(embeddings, torch.Tensor):
                embeddings = embeddings.cpu().numpy()
            
            # Convert to list of lists
            if hasattr(embeddings, 'tolist'):
                result = embeddings.tolist()
            else:
                result = list(embeddings)
            
            # Ensure all are lists of floats
            return [[float(x) for x in emb] for emb in result]
    
    async def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI API."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    async def _get_local_embedding(self, text: str) -> List[float]:
        """
        Get embedding from local sentence-transformers model.
        
        Note: Model encoding is synchronous, but we make this async for compatibility.
        """
        import asyncio
        
        # Run synchronous operation in thread pool for async compatibility
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self.model.encode(text, convert_to_numpy=False)
        )
        
        # Handle tensor conversion (MPS/CPU/CUDA compatibility)
        if TORCH_AVAILABLE and isinstance(embedding, torch.Tensor):
            embedding = embedding.cpu().numpy()
        elif hasattr(embedding, 'tolist'):
            embedding = embedding.tolist()
        
        # Ensure it's a list of floats
        if isinstance(embedding, (list, tuple)):
            return [float(x) for x in embedding]
        else:
            return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
    
    @staticmethod
    def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Ensure we have proper Python lists (not tensors or numpy arrays)
        if not isinstance(embedding1, list):
            embedding1 = [float(x) for x in embedding1]
        if not isinstance(embedding2, list):
            embedding2 = [float(x) for x in embedding2]
        
        vec1 = np.array(embedding1, dtype=np.float32)
        vec2 = np.array(embedding2, dtype=np.float32)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)


# Factory function for easy initialization
def create_embedding_service(
    use_openai: bool = False,
    openai_api_key: Optional[str] = None
) -> EmbeddingService:
    """
    Factory function to create EmbeddingService instance.
    
    Args:
        use_openai: Whether to use OpenAI embeddings
        openai_api_key: OpenAI API key (if using OpenAI)
        
    Returns:
        Configured EmbeddingService instance
    """
    return EmbeddingService(
        use_openai=use_openai,
        openai_api_key=openai_api_key
    )

