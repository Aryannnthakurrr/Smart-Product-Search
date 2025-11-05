"""
Semantic search engine for construction materials using sentence transformers.
"""
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

import numpy as np
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient

# Load environment variables
load_dotenv()


class MaterialSemanticSearch:
    """Semantic search engine for construction materials."""
    
    def __init__(
        self, 
        cache_dir: str = "cache",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the semantic search engine.
        
        Args:
            cache_dir: Directory to store cached embeddings
            model_name: Name of the sentence transformer model to use
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.model_name = model_name
        
        # MongoDB connection
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.mongodb_database = os.getenv("MONGODB_DATABASE", "product")
        self.mongodb_collection = os.getenv("MONGODB_COLLECTION", "Material-Mover")
        
        # Cache file paths
        self.embeddings_cache = self.cache_dir / "material_embeddings.pkl"
        self.materials_cache = self.cache_dir / "materials_data.pkl"
        
        # Load model
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        # Load or build cache
        self._load_or_build_cache()
        
    def _load_or_build_cache(self):
        """Load cached embeddings or build them if not available."""
        if self.embeddings_cache.exists() and self.materials_cache.exists():
            print("Loading cached embeddings...")
            with open(self.embeddings_cache, "rb") as f:
                self.embeddings = pickle.load(f)
            with open(self.materials_cache, "rb") as f:
                self.materials = pickle.load(f)
            print(f"Loaded {len(self.materials)} construction materials from cache.")
        else:
            print("Building embeddings cache...")
            self._build_cache()
            
    def _build_cache(self):
        """Build embeddings for all construction materials from MongoDB and cache them."""
        # Connect to MongoDB
        print(f"Connecting to MongoDB...")
        client = MongoClient(self.mongodb_uri)
        db = client[self.mongodb_database]
        collection = db[self.mongodb_collection]
        
        # Fetch all materials
        print(f"Fetching construction materials from MongoDB...")
        print(f"Database: {self.mongodb_database}, Collection: {self.mongodb_collection}")
        
        # Check if collection exists and has documents
        total_docs = collection.count_documents({})
        print(f"Total documents in collection: {total_docs}")
        
        cursor = collection.find({})
        self.materials = []
        
        for doc in cursor:
            # Convert ObjectId to string for JSON serialization
            material = {
                "id": str(doc["_id"]),
                "title": doc.get("title", ""),
                "description": doc.get("description", ""),
                "price": doc.get("price", 0),
                "quantity": doc.get("quantity", 0),
                "category": doc.get("category", ""),
                "image": doc.get("image", "")
            }
            self.materials.append(material)
        
        client.close()
        print(f"Loaded {len(self.materials)} construction materials from database.")
        
        # Create text representations for embedding
        material_texts = []
        for material in self.materials:
            # Combine title, category, and description for better semantic matching
            text = f"{material['title']}. Category: {material['category']}. {material['description']}"
            material_texts.append(text)
        
        # Generate embeddings
        print("Generating embeddings... This may take a few minutes on first run.")
        self.embeddings = self.model.encode(
            material_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Save to cache
        print("Saving embeddings to cache...")
        with open(self.embeddings_cache, "wb") as f:
            pickle.dump(self.embeddings, f)
        with open(self.materials_cache, "wb") as f:
            pickle.dump(self.materials, f)
        
        print("Cache built successfully!")
        
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for construction materials semantically similar to the query.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            min_score: Minimum similarity score (0-1) for results
            
        Returns:
            List of material dictionaries with similarity scores
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
                material = self.materials[idx].copy()
                material["similarity_score"] = round(score, 4)
                results.append(material)
        
        return results
    
    def rebuild_cache(self):
        """Force rebuild of the embeddings cache."""
        print("Rebuilding cache...")
        if self.embeddings_cache.exists():
            self.embeddings_cache.unlink()
        if self.materials_cache.exists():
            self.materials_cache.unlink()
        self._build_cache()
