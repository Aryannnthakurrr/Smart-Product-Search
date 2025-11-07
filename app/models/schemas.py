"""Pydantic models for API requests and responses"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Material(BaseModel):
    """Material data model"""
    id: str = Field(alias="_id")
    title: str
    description: str
    category: str
    price: float
    quantity: Optional[int] = 0
    brand: Optional[str] = ""
    image: Optional[str] = ""
    score: Optional[float] = None
    
    class Config:
        populate_by_name = True


class SearchRequest(BaseModel):
    """Search request payload"""
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    min_score: float = Field(0.3, ge=0.0, le=1.0, description="Minimum similarity score")


class SearchResponse(BaseModel):
    """Search response payload"""
    query: str
    results: List[Material]
    total: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    materials_loaded: int
    model: str
