"""
FastAPI-based semantic construction material search API.
"""
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from lib.semantic_search import MaterialSemanticSearch


# Global search engine instance
search_engine: Optional[MaterialSemanticSearch] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the search engine on startup."""
    global search_engine
    print("Initializing semantic search engine...")
    search_engine = MaterialSemanticSearch()
    print("Search engine ready!")
    yield
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Construction Material Semantic Search API",
    description="Search for construction materials using natural language queries powered by sentence transformers",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class Material(BaseModel):
    """Construction material model."""
    id: str
    title: str
    description: str
    price: float
    quantity: int
    category: str
    image: str
    similarity_score: float = Field(..., description="Similarity score between 0 and 1")


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Natural language search query", min_length=1)
    top_k: int = Field(5, description="Number of results to return", ge=1, le=50)
    min_score: float = Field(0.0, description="Minimum similarity score", ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: List[Material]
    count: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    total_materials: int


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Construction Material Semantic Search API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the API status and total number of construction materials indexed.
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    return {
        "status": "healthy",
        "total_materials": len(search_engine.materials)
    }


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search_materials(
    query: str = Query(..., description="Natural language search query", min_length=1),
    top_k: int = Query(5, description="Number of results to return", ge=1, le=50),
    min_score: float = Query(0.0, description="Minimum similarity score (0-1)", ge=0.0, le=1.0)
):
    """
    Search for construction materials using semantic similarity.
    
    This endpoint accepts a natural language query and returns the most semantically
    similar construction materials from the database.
    
    **Example queries:**
    - "cement for foundation work"
    - "steel rods for reinforcement"
    - "waterproofing material for roof"
    - "paint for exterior walls"
    - "tiles for bathroom flooring"
    
    **Parameters:**
    - **query**: Your search query in natural language
    - **top_k**: How many results you want (1-50, default: 5)
    - **min_score**: Minimum similarity score threshold (0-1, default: 0.0)
    
    **Returns:**
    - List of construction materials with their similarity scores, prices, and details
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        results = search_engine.search(
            query=query,
            top_k=top_k,
            min_score=min_score
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_materials_post(request: SearchRequest):
    """
    Search for construction materials using semantic similarity (POST version).
    
    Same as GET /search but accepts a JSON body instead of query parameters.
    Useful for longer queries or when building API clients.
    
    **Example request body:**
    ```json
    {
        "query": "cement bags for foundation",
        "top_k": 10,
        "min_score": 0.3
    }
    ```
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        results = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score
        )
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/rebuild-cache", tags=["Admin"])
async def rebuild_cache():
    """
    Rebuild ALL embeddings from scratch.
    
    This removes all existing embeddings from MongoDB and regenerates them.
    Use this if you want to:
    - Change the embedding model
    - Fix corrupted embeddings
    - Force a complete refresh
    
    **Warning:** This is a heavy operation and will block the API while running.
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        search_engine.rebuild_cache()
        return {
            "status": "success",
            "message": "All embeddings rebuilt successfully from MongoDB",
            "total_materials": len(search_engine.materials)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache rebuild error: {str(e)}")


@app.post("/webhooks/product-created", tags=["Webhooks"])
async def product_created_webhook(product_id: str):
    """
    Webhook to generate embedding when a new product is added to MongoDB.
    
    Your friend's MERN app should call this endpoint whenever they add a new product.
    
    **Example:**
    ```javascript
    // After inserting new product in MongoDB
    const newProduct = await Product.create({...});
    
    // Notify semantic search API
    await axios.post('http://your-api.com/webhooks/product-created', {
      product_id: newProduct._id.toString()
    });
    ```
    
    **Parameters:**
    - **product_id**: The MongoDB ObjectId of the newly created product
    
    **Returns:**
    - Success message with product details
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        success = search_engine.add_new_material(product_id)
        if success:
            return {
                "status": "success",
                "message": f"Embedding generated for product {product_id}",
                "total_materials": len(search_engine.materials)
            }
        else:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")


@app.post("/webhooks/product-updated", tags=["Webhooks"])
async def product_updated_webhook(product_id: str):
    """
    Webhook to update embedding when a product's details are changed.
    
    Call this when title, description, or category is updated in MongoDB.
    
    **Example:**
    ```javascript
    // After updating product in MongoDB
    await Product.findByIdAndUpdate(productId, { title: "New Title" });
    
    // Notify semantic search API
    await axios.post('http://your-api.com/webhooks/product-updated', {
      product_id: productId
    });
    ```
    
    **Parameters:**
    - **product_id**: The MongoDB ObjectId of the updated product
    
    **Returns:**
    - Success message with updated details
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        success = search_engine.update_material_embedding(product_id)
        if success:
            return {
                "status": "success",
                "message": f"Embedding updated for product {product_id}",
                "total_materials": len(search_engine.materials)
            }
        else:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating embedding: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
