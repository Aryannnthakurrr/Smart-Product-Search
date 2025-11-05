"""
Semantic search engine for movies using sentence transformers.
"""
import json
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer


class MovieSemanticSearch:
    """Semantic search engine for movies."""
    
    def __init__(
        self, 
        movies_path: str = "data/movies.json",
        cache_dir: str = "cache",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the semantic search engine.
        
        Args:
            movies_path: Path to the movies JSON file
            cache_dir: Directory to store cached embeddings
            model_name: Name of the sentence transformer model to use
        """
        self.movies_path = movies_path
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.model_name = model_name
        
        # Cache file paths
        self.embeddings_cache = self.cache_dir / "movie_embeddings.pkl"
        self.movies_cache = self.cache_dir / "movies_data.pkl"
        
        # Load model
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        # Load or build cache
        self._load_or_build_cache()
        
    def _load_or_build_cache(self):
        """Load cached embeddings or build them if not available."""
        if self.embeddings_cache.exists() and self.movies_cache.exists():
            print("Loading cached embeddings...")
            with open(self.embeddings_cache, "rb") as f:
                self.embeddings = pickle.load(f)
            with open(self.movies_cache, "rb") as f:
                self.movies = pickle.load(f)
            print(f"Loaded {len(self.movies)} movies from cache.")
        else:
            print("Building embeddings cache...")
            self._build_cache()
            
    def _build_cache(self):
        """Build embeddings for all movies and cache them."""
        # Load movies
        print(f"Loading movies from {self.movies_path}...")
        with open(self.movies_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.movies = data["movies"]
        
        print(f"Loaded {len(self.movies)} movies.")
        
        # Create text representations for embedding
        movie_texts = []
        for movie in self.movies:
            # Combine title and description for better semantic matching
            text = f"{movie['title']}. {movie['description']}"
            movie_texts.append(text)
        
        # Generate embeddings
        print("Generating embeddings... This may take a few minutes on first run.")
        self.embeddings = self.model.encode(
            movie_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Save to cache
        print("Saving embeddings to cache...")
        with open(self.embeddings_cache, "wb") as f:
            pickle.dump(self.embeddings, f)
        with open(self.movies_cache, "wb") as f:
            pickle.dump(self.movies, f)
        
        print("Cache built successfully!")
        
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for movies semantically similar to the query.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            min_score: Minimum similarity score (0-1) for results
            
        Returns:
            List of movie dictionaries with similarity scores
        """
        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= min_score:
                movie = self.movies[idx].copy()
                movie["similarity_score"] = round(score, 4)
                results.append(movie)
        
        return results
    
    def rebuild_cache(self):
        """Force rebuild of the embeddings cache."""
        print("Rebuilding cache...")
        if self.embeddings_cache.exists():
            self.embeddings_cache.unlink()
        if self.movies_cache.exists():
            self.movies_cache.unlink()
        self._build_cache()
