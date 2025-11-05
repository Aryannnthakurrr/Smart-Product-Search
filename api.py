"""
FastAPI-based semantic movie search API.
"""
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from lib.semantic_search import MovieSemanticSearch


# Global search engine instance
search_engine: Optional[MovieSemanticSearch] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the search engine on startup."""
    global search_engine
    print("Initializing semantic search engine...")
    search_engine = MovieSemanticSearch()
    print("Search engine ready!")
    yield
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Movie Semantic Search API",
    description="Search for movies using natural language queries powered by sentence transformers",
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
class Movie(BaseModel):
    """Movie model."""
    id: int
    title: str
    description: str
    similarity_score: float = Field(..., description="Similarity score between 0 and 1")


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Natural language search query", min_length=1)
    top_k: int = Field(5, description="Number of results to return", ge=1, le=50)
    min_score: float = Field(0.0, description="Minimum similarity score", ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: List[Movie]
    count: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    total_movies: int


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Movie Semantic Search API",
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
    
    Returns the API status and total number of movies indexed.
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    return {
        "status": "healthy",
        "total_movies": len(search_engine.movies)
    }


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search_movies(
    query: str = Query(..., description="Natural language search query", min_length=1),
    top_k: int = Query(5, description="Number of results to return", ge=1, le=50),
    min_score: float = Query(0.0, description="Minimum similarity score (0-1)", ge=0.0, le=1.0)
):
    """
    Search for movies using semantic similarity.
    
    This endpoint accepts a natural language query and returns the most semantically
    similar movies from the database.
    
    **Example queries:**
    - "action movie with explosions"
    - "romantic comedy set in new york"
    - "sci-fi thriller about time travel"
    - "family friendly animated adventure"
    
    **Parameters:**
    - **query**: Your search query in natural language
    - **top_k**: How many results you want (1-50, default: 5)
    - **min_score**: Minimum similarity score threshold (0-1, default: 0.0)
    
    **Returns:**
    - List of movies with their similarity scores
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
async def search_movies_post(request: SearchRequest):
    """
    Search for movies using semantic similarity (POST version).
    
    Same as GET /search but accepts a JSON body instead of query parameters.
    Useful for longer queries or when building API clients.
    
    **Example request body:**
    ```json
    {
        "query": "action movie with explosions",
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
    Rebuild the embeddings cache.
    
    Use this endpoint if you've updated the movies data and want to regenerate
    the embeddings. This operation may take several minutes.
    
    **Warning:** This is a heavy operation and will block the API while running.
    """
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        search_engine.rebuild_cache()
        return {
            "status": "success",
            "message": "Cache rebuilt successfully",
            "total_movies": len(search_engine.movies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache rebuild error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
