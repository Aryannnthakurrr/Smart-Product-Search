"""
Semantic search engine for construction materials using sentence transformers.
Embeddings are stored in MongoDB for persistence and fast retrieval.
"""
import os
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

import numpy as np
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()


class MaterialSemanticSearch:
    """Semantic search engine for construction materials with MongoDB caching."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic search engine.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        
        # MongoDB connection
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.mongodb_database = os.getenv("MONGODB_DATABASE", "product")
        self.mongodb_collection = os.getenv("MONGODB_COLLECTION", "products")
        
        # Connect to MongoDB
        print(f"Connecting to MongoDB...")
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_database]
        self.collection = self.db[self.mongodb_collection]
        
        # Load model
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        # Load materials and embeddings from MongoDB
        self._load_from_mongodb()
        
    def _load_from_mongodb(self):
        """Load materials and embeddings from MongoDB (with auto-generation)."""
        print(f"📊 Loading materials from MongoDB...")
        print(f"Database: {self.mongodb_database}, Collection: {self.mongodb_collection}")
        
        # Count total documents
        total_docs = self.collection.count_documents({})
        print(f"Total documents in collection: {total_docs}")
        
        if total_docs == 0:
            print("⚠️  No materials found in database!")
            self.materials = []
            self.embeddings = np.array([])
            return
        
        # Fetch all products
        products = list(self.collection.find({}))
        
        self.materials = []
        embeddings_list = []
        products_without_embeddings = []
        
        # Separate products with and without embeddings
        for product in products:
            material_data = {
                'id': str(product['_id']),
                'title': product.get('title', ''),
                'description': product.get('description', ''),
                'price': product.get('price', 0),
                'quantity': product.get('quantity', 0),
                'category': product.get('category', ''),
                'image': product.get('image', '')
            }
            
            # Check if embedding exists and is valid
            if 'embedding' in product and product['embedding'] and len(product['embedding']) > 0:
                # Has embedding - use it
                self.materials.append(material_data)
                embeddings_list.append(product['embedding'])
            else:
                # No embedding - need to generate
                products_without_embeddings.append((product['_id'], material_data))
        
        print(f"✅ Loaded {len(self.materials)} materials with embeddings")
        
        # Generate embeddings for products that don't have them
        if products_without_embeddings:
            print(f"🔄 Generating embeddings for {len(products_without_embeddings)} new products...")
            self._generate_and_save_embeddings(products_without_embeddings, embeddings_list)
        
        # Convert to numpy array
        self.embeddings = np.array(embeddings_list)
        print(f"✅ Ready! {len(self.materials)} materials indexed for semantic search")
    
    def _generate_and_save_embeddings(self, products_list, embeddings_list):
        """Generate embeddings for products and save them to MongoDB."""
        batch_size = 32
        
        for i, (product_id, material_data) in enumerate(products_list):
            # Create text for embedding
            text = f"{material_data['title']} {material_data['category']} {material_data['description']}"
            
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True).tolist()
            
            # Update MongoDB with embedding
            self.collection.update_one(
                {'_id': product_id},
                {
                    '$set': {
                        'embedding': embedding,
                        'embedding_generated_at': datetime.utcnow(),
                        'embedding_model': self.model_name
                    }
                }
            )
            
            # Add to in-memory cache
            self.materials.append(material_data)
            embeddings_list.append(embedding)
            
            # Progress indicator
            if (i + 1) % 10 == 0 or (i + 1) == len(products_list):
                print(f"  Generated {i + 1}/{len(products_list)} embeddings...")
        
        print(f"✅ Generated and saved {len(products_list)} embeddings to MongoDB")
        
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
    
    def add_new_material(self, product_id: str):
        """
        Generate and store embedding for a newly added product.
        This should be called when a new product is added to MongoDB.
        
        Args:
            product_id: MongoDB ObjectId as string
        """
        print(f"🔄 Adding new material: {product_id}")
        
        # Fetch the product from MongoDB
        try:
            product = self.collection.find_one({'_id': ObjectId(product_id)})
            if not product:
                print(f"❌ Product {product_id} not found in database")
                return False
            
            # Check if it already has an embedding
            if 'embedding' in product and product['embedding']:
                print(f"⚠️  Product {product_id} already has an embedding")
                return True
            
            # Create material data
            material_data = {
                'id': str(product['_id']),
                'title': product.get('title', ''),
                'description': product.get('description', ''),
                'price': product.get('price', 0),
                'quantity': product.get('quantity', 0),
                'category': product.get('category', ''),
                'image': product.get('image', '')
            }
            
            # Generate text for embedding
            text = f"{material_data['title']} {material_data['category']} {material_data['description']}"
            
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True).tolist()
            
            # Save to MongoDB
            self.collection.update_one(
                {'_id': ObjectId(product_id)},
                {
                    '$set': {
                        'embedding': embedding,
                        'embedding_generated_at': datetime.utcnow(),
                        'embedding_model': self.model_name
                    }
                }
            )
            
            # Add to in-memory cache
            self.materials.append(material_data)
            self.embeddings = np.vstack([self.embeddings, np.array(embedding)])
            
            print(f"✅ Added new material: {material_data['title']}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding material: {e}")
            return False
    
    def update_material_embedding(self, product_id: str):
        """
        Regenerate embedding for an existing product (e.g., after title/description update).
        
        Args:
            product_id: MongoDB ObjectId as string
        """
        print(f"🔄 Updating material embedding: {product_id}")
        
        try:
            # Remove from in-memory cache
            self.materials = [m for m in self.materials if m['id'] != product_id]
            
            # Remove old embedding from MongoDB
            self.collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$unset': {'embedding': '', 'embedding_generated_at': ''}}
            )
            
            # Reload everything (simpler than trying to update in place)
            self._load_from_mongodb()
            
            print(f"✅ Updated material embedding")
            return True
            
        except Exception as e:
            print(f"❌ Error updating material: {e}")
            return False
    
    def rebuild_cache(self):
        """
        Force rebuild all embeddings from scratch.
        This removes all existing embeddings from MongoDB and regenerates them.
        """
        print("🔄 Rebuilding all embeddings from scratch...")
        
        # Remove all embeddings from MongoDB
        result = self.collection.update_many(
            {},
            {'$unset': {'embedding': '', 'embedding_generated_at': '', 'embedding_model': ''}}
        )
        
        print(f"Cleared {result.modified_count} embeddings from MongoDB")
        
        # Reload and regenerate
        self._load_from_mongodb()
        
        print("✅ Cache rebuilt successfully!")
