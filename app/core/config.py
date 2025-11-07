"""Application configuration"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "product")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION", "products")
    
    # Model
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # API
    API_TITLE: str = "Construction Materials Semantic Search"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Semantic search microservice for construction materials catalog"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    def validate(self) -> None:
        """Validate required settings"""
        if not self.MONGODB_URI:
            raise ValueError("MONGODB_URI is required in environment variables")


settings = Settings()
