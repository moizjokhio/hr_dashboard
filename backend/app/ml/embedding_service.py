"""
Embedding service using BGE models for semantic search
Runs entirely locally with GPU acceleration
"""

import os
from typing import List, Optional, Union
import numpy as np
from pathlib import Path

from app.core.config import settings


class EmbeddingService:
    """
    Local embedding service using BGE-Large or BGE-M3
    Provides semantic embeddings for search and similarity
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_loaded = False
        self.embedding_dim = settings.ai.EMBEDDING_BATCH_SIZE
    
    def load_model(self):
        """
        Load embedding model from local disk
        Uses GPU if available, falls back to CPU
        """
        if self.model_loaded:
            return
        
        import torch
        from transformers import AutoTokenizer, AutoModel
        
        # Determine device
        if settings.ai.USE_GPU and torch.cuda.is_available():
            self.device = torch.device("cuda")
            # Set GPU memory fraction
            torch.cuda.set_per_process_memory_fraction(
                settings.ai.GPU_MEMORY_FRACTION
            )
        else:
            self.device = torch.device("cpu")
        
        model_path = Path(settings.ai.EMBEDDING_MODEL_PATH)
        
        # Load from local path if exists, otherwise download
        if model_path.exists():
            self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            self.model = AutoModel.from_pretrained(str(model_path))
        else:
            # Download and cache
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.ai.EMBEDDING_MODEL_NAME
            )
            self.model = AutoModel.from_pretrained(
                settings.ai.EMBEDDING_MODEL_NAME
            )
            # Save locally for future use
            model_path.parent.mkdir(parents=True, exist_ok=True)
            self.tokenizer.save_pretrained(str(model_path))
            self.model.save_pretrained(str(model_path))
        
        self.model.to(self.device)
        self.model.eval()
        self.model_loaded = True
        
        # Get embedding dimension from model
        self.embedding_dim = self.model.config.hidden_size
    
    def _mean_pooling(self, model_output, attention_mask):
        """Apply mean pooling to get sentence embeddings"""
        import torch
        
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(
            token_embeddings.size()
        ).float()
        
        return torch.sum(
            token_embeddings * input_mask_expanded, 1
        ) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        batch_size: int = None
    ) -> np.ndarray:
        """
        Encode texts to embeddings
        
        Args:
            texts: Single text or list of texts to encode
            normalize: Whether to L2 normalize embeddings
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        import torch
        
        if not self.model_loaded:
            self.load_model()
        
        if isinstance(texts, str):
            texts = [texts]
        
        batch_size = batch_size or settings.ai.EMBEDDING_BATCH_SIZE
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Tokenize
            encoded = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # Move to device
            encoded = {k: v.to(self.device) for k, v in encoded.items()}
            
            # Get embeddings
            with torch.no_grad():
                model_output = self.model(**encoded)
                embeddings = self._mean_pooling(
                    model_output, 
                    encoded['attention_mask']
                )
                
                if normalize:
                    embeddings = torch.nn.functional.normalize(
                        embeddings, p=2, dim=1
                    )
                
                all_embeddings.append(embeddings.cpu().numpy())
        
        return np.vstack(all_embeddings)
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a search query with instruction prefix (for BGE models)
        """
        # BGE models recommend adding instruction for queries
        instruction = "Represent this sentence for searching relevant passages: "
        return self.encode(instruction + query)[0]
    
    def similarity(
        self,
        query_embedding: np.ndarray,
        corpus_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and corpus
        
        Args:
            query_embedding: Single query embedding
            corpus_embeddings: Matrix of corpus embeddings
            
        Returns:
            Array of similarity scores
        """
        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Cosine similarity (embeddings are already normalized)
        similarities = np.dot(corpus_embeddings, query_embedding.T).flatten()
        return similarities
    
    def find_similar(
        self,
        query: str,
        corpus: List[str],
        top_k: int = 5
    ) -> List[dict]:
        """
        Find most similar texts from corpus
        
        Args:
            query: Query text
            corpus: List of texts to search
            top_k: Number of results to return
            
        Returns:
            List of dicts with text, score, and index
        """
        query_emb = self.encode_query(query)
        corpus_emb = self.encode(corpus)
        
        scores = self.similarity(query_emb, corpus_emb)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = [
            {
                "text": corpus[idx],
                "score": float(scores[idx]),
                "index": int(idx)
            }
            for idx in top_indices
        ]
        
        return results
    
    def unload_model(self):
        """Unload model to free GPU memory"""
        import torch
        
        if self.model is not None:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self.model_loaded = False
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# Singleton instance
embedding_service = EmbeddingService()
