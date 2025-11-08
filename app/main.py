"""FastAPI application for construction materials semantic search"""
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.schemas import Material, SearchRequest, SearchResponse, HealthResponse, HybridSearchRequest
from app.services.hybrid_search import HybridSearchEngine


# Global search engine instance
search_engine: Optional[HybridSearchEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global search_engine
    
    print("Initializing hybrid search engine...")
    search_engine = HybridSearchEngine()
    search_engine.initialize()
    print("Search engine ready!")
    
    yield
    
    print("Shutting down...")
    if search_engine:
        search_engine.shutdown()


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# ===== CORS CONFIGURATION FOR WiFi TESTING (Lines 36-48) =====
# ADDED: Enable Cross-Origin Resource Sharing for your friend's MERN app
# Your friend's React frontend (192.168.0.x:3000) can now make requests to your API (192.168.0.x:8000)
# This allows requests from any device on the same WiFi network
# 
# Details:
# - allow_origins: Allows requests from friend's React dev server on port 3000
# - allow_credentials: Allows cookies to be sent with requests
# - allow_methods: ["*"] Allows GET, POST, PUT, DELETE, etc.
# - allow_headers: ["*"] Allows any headers in the request
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # See app/core/config.py (Lines 25-32) for allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ===== END CORS CONFIGURATION =====



@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "endpoints": {
            "search": "/search",
            "health": "/health",
            "rebuild_cache": "/rebuild-cache",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Check API health and return statistics"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    stats = search_engine.get_stats()
    return {
        "status": "healthy",
        "materials_loaded": stats["semantic_materials"],
        "model": stats["model"]
    }


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search_get(
    query: str = Query(..., description="Natural language search query", min_length=1),
    top_k: int = Query(5, description="Number of results to return", ge=1, le=50),
    min_score: float = Query(0.3, description="Minimum combined score", ge=0.0, le=1.0),
    semantic_weight: float = Query(0.6, description="Weight for semantic search", ge=0.0, le=1.0),
    keyword_weight: float = Query(0.4, description="Weight for keyword search", ge=0.0, le=1.0)
):
    """
    Hybrid search for construction materials using semantic + keyword matching
    
    Combines:
    - Semantic search (BERT embeddings + cosine similarity)
    - Keyword search (BM25 ranking)
    
    Example queries:
    - cement for foundation work
    - steel rods for reinforcement
    - waterproofing material for roof
    - paint for exterior walls
    - tiles for bathroom flooring
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        results = search_engine.search(query, top_k, min_score, semantic_weight, keyword_weight)
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_post(request: HybridSearchRequest):
    """Hybrid search for construction materials using JSON request body"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        results = search_engine.search(
            request.query, 
            request.top_k, 
            request.min_score,
            request.semantic_weight,
            request.keyword_weight
        )
        return {
            "query": request.query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/recommend", tags=["Search"])
async def recommend_products(
    query: str = Query(..., description="Natural language search query", min_length=1)
):
    """
    Get top 10 recommended product IDs based on hybrid search
    
    Returns only product IDs - optimized for clean integration
    
    Default parameters:
    - top_k: 10
    - semantic_weight: 0.7 (prioritize meaning)
    - keyword_weight: 0.3 (ensure exact matches)
    - min_score: 0.3
    
    Example queries:
    - cement for foundation work
    - steel rods for reinforcement
    - waterproofing material
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        results = search_engine.search(
            query=query,
            top_k=10,
            min_score=0.3,
            semantic_weight=0.7,
            keyword_weight=0.3
        )
        
        # Extract only product IDs
        product_ids = [result["_id"] for result in results]
        
        return {
            "product_ids": product_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.post("/rebuild-cache", tags=["Admin"])
async def rebuild_cache():
    """Rebuild semantic embeddings and BM25 keyword index from scratch"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        # Rebuild semantic embeddings
        semantic_success = search_engine.semantic_engine.rebuild_cache()
        # Rebuild keyword index
        keyword_success = search_engine.rebuild_keyword_cache()
        
        if semantic_success and keyword_success:
            stats = search_engine.get_stats()
            return {
                "status": "success",
                "message": "All embeddings and keyword index rebuilt",
                "semantic_materials": stats["semantic_materials"],
                "keyword_materials": stats["keyword_materials"]
            }
        else:
            raise HTTPException(status_code=500, detail="Cache rebuild failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")


@app.post("/webhooks/product-created", tags=["Webhooks"])
async def product_created(product_id: str):
    """Generate embedding for newly created product"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        success = search_engine.add_material(product_id)
        if success:
            stats = search_engine.get_stats()
            return {
                "status": "success",
                "message": f"Embedding generated for product {product_id}",
                "materials_loaded": stats["materials_loaded"]
            }
        else:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add material: {str(e)}")


@app.post("/webhooks/product-updated", tags=["Webhooks"])
async def product_updated(product_id: str):
    """Update embedding for modified product"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        success = search_engine.update_material(product_id)
        if success:
            stats = search_engine.get_stats()
            return {
                "status": "success",
                "message": f"Embedding updated for product {product_id}",
                "materials_loaded": stats["materials_loaded"]
            }
        else:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update material: {str(e)}")
