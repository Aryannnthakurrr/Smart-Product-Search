"""FastAPI application for construction materials semantic search"""
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.schemas import Material, SearchRequest, SearchResponse, HealthResponse
from app.services.search import SemanticSearchEngine


# Global search engine instance
search_engine: Optional[SemanticSearchEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global search_engine
    
    print("Initializing semantic search engine...")
    search_engine = SemanticSearchEngine()
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        "materials_loaded": stats["materials_loaded"],
        "model": stats["model"]
    }


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search_get(
    query: str = Query(..., description="Natural language search query", min_length=1),
    top_k: int = Query(5, description="Number of results to return", ge=1, le=50),
    min_score: float = Query(0.3, description="Minimum similarity score", ge=0.0, le=1.0)
):
    """
    Search for construction materials using semantic similarity
    
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
        results = search_engine.search(query, top_k, min_score)
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_post(request: SearchRequest):
    """Search for construction materials using JSON request body"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        results = search_engine.search(request.query, request.top_k, request.min_score)
        return {
            "query": request.query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/rebuild-cache", tags=["Admin"])
async def rebuild_cache():
    """Rebuild all embeddings from scratch"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        success = search_engine.rebuild_cache()
        if success:
            stats = search_engine.get_stats()
            return {
                "status": "success",
                "message": "All embeddings rebuilt",
                "materials_loaded": stats["materials_loaded"]
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
