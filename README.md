# 🏗️ Construction Materials Semantic Search API

A high-performance FastAPI microservice that provides **intelligent semantic search** for construction materials using state-of-the-art natural language processing. Built with Sentence-BERT embeddings and MongoDB vector storage, this API understands the meaning behind search queries—not just keyword matches.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

- 🔍 **Semantic Search** - Natural language queries that understand context and meaning
- 🤖 **AI-Powered** - Sentence-BERT model (all-MiniLM-L6-v2) with 384-dimensional embeddings
- ⚡ **High Performance** - Sub-20ms search latency with cosine similarity
- 💾 **Persistent Storage** - MongoDB with automatic embedding caching
- 🔄 **Real-time Updates** - Webhook support for product creation/updates
- 📊 **Interactive API Docs** - Built-in Swagger UI at `/docs`

##  Quick Start

### Prerequisites

- **Python 3.11+** - Required for modern async features
- **MongoDB Atlas** - Free tier account ([Sign up here](https://www.mongodb.com/cloud/atlas))
- **2GB+ RAM** - For model loading and operations

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd materialmoversearch
```

2. **Install dependencies with uv**
```bash
# Install uv if you don't have it
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies (uv auto-manages virtual environment)
uv sync
```

> 💡 **Alternative with pip**: If you prefer using pip, run `python -m venv .venv`, activate it, then `pip install -r requirements.txt`

### Configuration

Create a `.env` file in the project root:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=product
MONGODB_COLLECTION=products
```

### Run the Server

```bash
# Using uv (recommended - auto-activates virtual environment)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or with standard uvicorn (if you activated .venv manually)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💡 Usage Examples

### Basic Search (GET)

```bash
curl "http://localhost:8000/search?query=cement%20for%20foundation&top_k=3"
```

**Response:**
```json
{
  "query": "cement for foundation",
  "results": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "title": "Portland Cement Type I",
      "description": "High-quality cement ideal for foundation and structural work",
      "category": "Cement",
      "price": 450.00,
      "brand": "UltraCem",
      "score": 0.8542
    }
  ],
  "total": 1
}
```

### Advanced Search (POST)

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "waterproofing material for bathroom",
    "top_k": 5,
    "min_score": 0.5
  }'
```

### Python Client

```python
import requests

response = requests.get(
    "http://localhost:8000/search",
    params={
        "query": "steel rods for reinforcement",
        "top_k": 5,
        "min_score": 0.4
    }
)

results = response.json()
for item in results["results"]:
    print(f"{item['title']} - Score: {item['score']:.2%}")
```

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "materials_loaded": 1247,
  "model": "all-MiniLM-L6-v2"
}
```

## 📚 API Reference

### Search Endpoints

#### `GET /search`
Semantic search with query parameters.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Natural language search query |
| `top_k` | integer | ❌ No | 5 | Number of results (1-50) |
| `min_score` | float | ❌ No | 0.3 | Minimum similarity score (0.0-1.0) |

**Example Queries:**
- `cement for foundation work`
- `steel rods for reinforcement`
- `waterproofing material for roof`
- `paint for exterior walls`

#### `POST /search`
Same as GET but with JSON body.

**Request Body:**
```json
{
  "query": "string (required)",
  "top_k": 5,
  "min_score": 0.3
}
```

### Admin Endpoints

#### `GET /health`
Health check with service statistics.

#### `POST /rebuild-cache`
Rebuild all embeddings from scratch (for bulk data updates).

#### `POST /webhooks/product-created`
Generate embedding for newly created product.

**Parameters:** `product_id` (MongoDB ObjectId)

#### `POST /webhooks/product-updated`
Update embedding for modified product.

**Parameters:** `product_id` (MongoDB ObjectId)

## 📁 Project Structure

```
materialmoversearch/
├── app/
│   ├── main.py                    # FastAPI application & routes
│   ├── core/
│   │   ├── config.py             # Settings & environment variables
│   │   └── database.py           # MongoDB connection manager
│   ├── models/
│   │   └── schemas.py            # Pydantic models for validation
│   └── services/
│       └── search.py             # Semantic search engine logic
├── .env                          # Environment configuration
├── requirements.txt              # Python dependencies
└── README.md                    # This file
```

### Core Components

**`app/main.py`** - FastAPI application setup, routes, CORS middleware, lifecycle management

**`app/core/config.py`** - Environment variables, application settings, model configuration

**`app/core/database.py`** - MongoDB client, CRUD operations, embedding persistence

**`app/models/schemas.py`** - Pydantic models for request/response validation

**`app/services/search.py`** - Sentence-BERT model, embedding generation, cosine similarity search

## 🔬 How It Works

### 1. Model Initialization
On startup, loads the `all-MiniLM-L6-v2` Sentence-BERT model (133MB) that converts text into 384-dimensional vectors.

### 2. Embedding Generation
For each material:
```python
text = f"{title} {category} {description}"
embedding = model.encode(text)  # Returns 384-dim vector
```

### 3. Vector Storage
Embeddings stored in MongoDB alongside material data:
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "title": "Portland Cement",
  "embedding": [0.123, -0.456, 0.789, ...],  // 384 floats
  "embedding_model": "all-MiniLM-L6-v2"
}
```

### 4. Search Process
1. Encode query into 384-dimensional vector
2. Calculate cosine similarity with all material embeddings
3. Rank results by similarity score
4. Filter by minimum score threshold
5. Return top-k most relevant materials

### 5. Cosine Similarity
Measures semantic similarity between vectors:
```
similarity = (query · material) / (||query|| × ||material||)
```
Result range: 0.0 (unrelated) to 1.0 (identical meaning)

## ⚡ Performance

| Metric | Value |
|--------|-------|
| **Cold Start** | 5-10 seconds |
| **Search Latency** | 10-20ms |
| **Throughput** | 50-100 req/s |
| **Memory Usage** | ~500MB |

### Optimization Tips

1. Use `min_score` filtering to reduce response size
2. Limit `top_k` to reasonable values (5-10)
3. Enable MongoDB indexes on frequently queried fields
4. Consider Redis for embedding cache in production
5. Use async clients for concurrent requests

## 🛠️ Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/) 0.115+** - Modern async web framework
- **[Sentence-Transformers](https://www.sbert.net/) 5.1+** - BERT-based semantic embeddings
- **[MongoDB Atlas](https://www.mongodb.com/cloud/atlas)** - Cloud database platform
- **[NumPy](https://numpy.org/) 2.3+** - Efficient vector operations
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server

### Model Details
- **Name**: `all-MiniLM-L6-v2`
- **Size**: 133MB
- **Dimensions**: 384
- **Performance**: 14.5x faster than BERT-base
- **Quality**: 96.3% of BERT-large performance

## License

MIT
