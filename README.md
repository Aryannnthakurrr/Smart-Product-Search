# 🏗️ Material Mover - Hybrid Search Engine

A production-grade FastAPI microservice for intelligent construction materials search. Combines **semantic understanding** (BERT embeddings) with **keyword precision** (BM25) to deliver the best of both worlds.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Demo](https://img.shields.io/badge/🎯%20Live%20Demo-View%20Project-0ea5e9?style=flat)](https://aryanthakur.vercel.app/projects/smart-product-search.html)

**Status:** ✅ Production-Ready | **Performance:** ⚡ 50-70 QPS | **Memory:** 💾 ~42MB for 465 materials

## ✨ Core Features

- 🎯 **Hybrid Search Engine** - Combines semantic + keyword algorithms for superior relevance
- 🔍 **Semantic Search** - BERT embeddings (384-dim) with cosine similarity for contextual understanding
- 🔑 **Keyword Search** - BM25 ranking for exact terms, acronyms, and brand names
- ⚖️ **Customizable Weights** - Adjust semantic/keyword balance (0.0-1.0) per query
- ⚡ **High Performance** - 14.56ms avg semantic, 25.25ms avg keyword, 46.95ms hybrid
- 📊 **Detailed Scoring** - Semantic, keyword, and combined scores with transparency
- 🎁 **Clean Recommendations API** - Simple endpoint returning product IDs only
- 💾 **Persistent Storage** - MongoDB Atlas with automatic embedding caching
- 🏥 **Health Checks** - System status and material count endpoints
- � **Interactive Docs** - Auto-generated Swagger UI at `/docs`, ReDoc at `/redoc`

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** - Modern async runtime
- **MongoDB Atlas** - Free tier account ([Sign up](https://www.mongodb.com/cloud/atlas))
- **2GB+ RAM** - For model loading and inference

### Installation (3 Steps)

**1. Clone & Navigate**
```bash
git clone <repository-url>
cd materialmoversearch
```

**2. Install Dependencies with `uv`** (Recommended)
```bash
# Install uv (if needed)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

**Alternative with pip:**
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

**3. Configure Environment**

Create `.env` in project root:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=product
MONGODB_COLLECTION=products
```

### Start the Server

```bash
# Using uv (auto-activates virtual environment)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
✅ Loaded 465 materials with embeddings
✅ Ready! 465 materials indexed for semantic search
✅ Loaded BM25 index from MongoDB with 465 materials
✅ Hybrid search engine ready!
```

**Access:**
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 💡 Usage Examples

### Example 1: Simple Recommendations
Get top 10 recommended product IDs (clean integration):
```bash
curl "http://localhost:8000/recommend?query=cement%20foundation"
```

**Response:**
```json
{
  "product_ids": ["673dc3d47f2a2c3aae0c2345", "673dc3d47f2a2c3aae0c2346", "673dc3d47f2a2c3aae0c2347"]
}
```

### Example 2: Full Hybrid Search
Get detailed results with scores:
```bash
curl "http://localhost:8000/search?query=cement%20foundation&top_k=3"
```

**Response:**
```json
{
  "query": "cement foundation",
  "results": [
    {
      "_id": "673dc3d47f2a2c3aae0c2345",
      "title": "Portland Cement Type I",
      "description": "High-quality cement ideal for foundation work",
      "category": "Cement",
      "price": 450.00,
      "semantic_score": 0.8542,
      "keyword_score": 0.7891,
      "combined_score": 0.8291
    }
  ],
  "total": 1
}
```

### Example 3: Natural Language (More Semantic)
For natural language queries, increase semantic weight:
```bash
curl "http://localhost:8000/search?query=materials%20for%20waterproofing&semantic_weight=0.8&keyword_weight=0.2"
```

### Example 4: Exact Terms (More Keyword)
For exact brand/part numbers, increase keyword weight:
```bash
curl "http://localhost:8000/search?query=Portland%20Type%20I&semantic_weight=0.3&keyword_weight=0.7"
```

### Example 5: Python Client
```python
import requests

# Simple recommendations
response = requests.get(
    "http://localhost:8000/recommend",
    params={"query": "steel rods for reinforcement"}
)
product_ids = response.json()["product_ids"]

# Detailed hybrid search with custom weights
response = requests.get(
    "http://localhost:8000/search",
    params={
        "query": "steel rods for reinforcement",
        "top_k": 5,
        "semantic_weight": 0.6,
        "keyword_weight": 0.4
    }
)

for item in response.json()["results"]:
    print(f"{item['title']}: {item['combined_score']:.2%}")
```

### Example 6: Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "materials_loaded": 465,
  "model": "all-MiniLM-L6-v2"
}
```

## 📚 API Reference

### Search Endpoints

#### `GET /recommend`
**Get top 10 recommended product IDs** (clean endpoint for simple integrations)

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | ✅ | Search query |

**Defaults:** Top 10 results | 70% semantic, 30% keyword | Min score: 0.3

**Response:** `{"product_ids": ["id1", "id2", ...]}`

---

#### `GET /search` & `POST /search`
**Detailed hybrid search** with full customization and scoring transparency

**Parameters:**
| Name | Type | Required | Default | Range | Description |
|------|------|----------|---------|-------|-------------|
| `query` | string | ✅ | — | — | Search query |
| `top_k` | integer | ❌ | 5 | 1-50 | Results to return |
| `min_score` | float | ❌ | 0.3 | 0.0-1.0 | Minimum combined score |
| `semantic_weight` | float | ❌ | 0.6 | 0.0-1.0 | Semantic algorithm weight |
| `keyword_weight` | float | ❌ | 0.4 | 0.0-1.0 | Keyword algorithm weight |

**Example Queries:**
- `"cement for foundation"` — Natural language
- `"steel rods reinforcement"` — Multiple terms
- `"Portland Type I"` — Brand/specific product
- `"waterproofing materials"` — Category search

**GET Request:**
```bash
curl "http://localhost:8000/search?query=cement&semantic_weight=0.7&top_k=5"
```

**POST Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cement foundation",
    "top_k": 5,
    "semantic_weight": 0.6,
    "keyword_weight": 0.4
  }'
```

**Response:**
```json
{
  "query": "cement foundation",
  "results": [
    {
      "_id": "ObjectId",
      "title": "Product Name",
      "description": "Product description",
      "category": "Category",
      "price": 450.00,
      "semantic_score": 0.8542,
      "keyword_score": 0.7891,
      "combined_score": 0.8291
    }
  ],
  "total": 1
}
```

---

#### `GET /health`
**System health and statistics**

**Response:**
```json
{
  "status": "healthy",
  "materials_loaded": 465,
  "model": "all-MiniLM-L6-v2"
}
```

---

### Admin Endpoints

#### `POST /rebuild-cache`
Rebuild semantic embeddings and BM25 index from MongoDB

```bash
curl -X POST "http://localhost:8000/rebuild-cache"
```

#### `POST /webhooks/product-created`
Generate embedding for new product

**Parameter:** `product_id` (MongoDB ObjectId)

#### `POST /webhooks/product-updated`
Update embedding for modified product

**Parameter:** `product_id` (MongoDB ObjectId)

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
│       ├── search.py             # Semantic search (BERT)
│       ├── keyword_search.py     # BM25 keyword search
│       └── hybrid_search.py      # Combines both engines
├── .env                          # Environment configuration
├── requirements.txt              # Python dependencies
└── README.md                    # This file
```

### Core Components

**`app/services/hybrid_search.py`** - Combines semantic and keyword search with weighted scoring

**`app/services/search.py`** - BERT embeddings, cosine similarity, vector operations

**`app/services/keyword_search.py`** - BM25 ranking, inverted index, term frequency analysis

**`app/main.py`** - FastAPI routes, middleware, lifecycle management

**`app/core/database.py`** - MongoDB operations, embedding persistence

**`app/models/schemas.py`** - Request/response validation with Pydantic

## � Support & Documentation

- **Swagger API Docs:** http://localhost:8000/docs (when running)
- **ReDoc:** http://localhost:8000/redoc (when running)
- **GitHub:** [Smart-Product-Search](https://github.com/Aryannnthakurrr/Smart-Product-Search)
- **Quick Start Guide:** See `QUICK_START.md` for detailed examples

---

**Built with ❤️ for intelligent product search** | MIT License

## ⚡ Performance Metrics

**Tested on:** Windows 11, Python 3.11, 465 materials | **3 consecutive test runs** (Nov 9, 2025)

### Throughput & Latency

| Algorithm | Avg Response | Range | QPS | Status |
|-----------|--------------|-------|-----|--------|
| **Semantic Search** | 14.56 ms | 10.32-39.27 ms | **69.94** | ✅ Fastest |
| **BM25 Keyword** | 25.25 ms | 20.79-45.40 ms | 39.62 | ✅ Stable |
| **Hybrid (60/40)** | 46.95 ms | 36.19-78.46 ms | 21.37 | ✅ Accurate |
| **Concurrent (48 req)** | 43.48 ms | 34.63-67.14 ms | ~23.7 | ✅ Predictable |

### Response Time Distribution (100 Queries)

```
Min:    31.98 ms (p0)
p50:    42.24 ms (median)
p90:    47.33 ms (90th percentile)
p95:    49.01 ms (95th percentile)  
p99:    70.90 ms (99th percentile)
Max:    70.90 ms (p100)
```

**Result:** 97% of requests complete in <50ms | 99% in <100ms ✅

### Memory Footprint

| Metric | Value |
|--------|-------|
| **Engine Memory** | 41.72 MB (465 materials) |
| **Per Material** | 91.88 KB |
| **For 1,000 materials** | ~92 MB |
| **For 10,000 materials** | ~920 MB |
| **For 50,000 materials** | ~4.6 GB |

### Index Statistics

- **BM25 Inverted Index:** 2,172 unique terms
- **Semantic Embeddings:** 465 × 384-dim vectors
- **Average Document Length:** 20.43 tokens
- **Model:** all-MiniLM-L6-v2 (133MB, 384-dimensional)

### Weight Configuration Guide

| Scenario | Semantic | Keyword | Example Query | Best For |
|----------|----------|---------|---------------|----------|
| Natural Language | 0.7-0.9 | 0.1-0.3 | "materials for waterproofing" | Meaning-based queries |
| **Balanced (Default)** | **0.6** | **0.4** | "cement for foundation" | **General purpose** |
| Exact Terms/Brands | 0.1-0.3 | 0.7-0.9 | "Portland Type I" | Brand/spec searches |

## � How It Works

### Algorithm Architecture

**1. Semantic Search (BERT)**
- Model: `all-MiniLM-L6-v2` (384-dim embeddings)
- Encodes query and materials into vectors
- Uses cosine similarity for ranking
- Understands meaning, context, synonyms
- Throughput: 69.94 QPS

**2. Keyword Search (BM25)**
- Builds inverted index from materials
- Ranks by term frequency & document frequency
- Formula: `BM25(q,d) = Σ IDF(qi) × TF(qi,d)`
- Excels at exact matches and acronyms
- Throughput: 39.62 QPS

**3. Score Combination**
```
combined_score = (semantic_weight × semantic_score) 
               + (keyword_weight × keyword_score)
Results ranked by combined_score (highest first)
```

### Search Flow
1. **Encode** query (semantic vector + keyword tokens)
2. **Calculate** semantic (cosine sim) and keyword (BM25) scores
3. **Normalize** both scores to [0, 1] range
4. **Combine** with weights: `0.6 × semantic + 0.4 × keyword` (default)
5. **Filter** by `min_score` threshold (default: 0.3)
6. **Rank** results and return top-k

---

## 🛠️ Tech Stack

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| **Framework** | FastAPI | 0.115+ | Async web API framework |
| **Embeddings** | Sentence-Transformers | 5.1+ | BERT-based semantic vectors |
| **Database** | MongoDB Atlas | Cloud | Material storage & indexing |
| **Numerics** | NumPy | 2.3+ | Vector operations |
| **NLP** | NLTK | 3.8+ | BM25 implementation |
| **Server** | Uvicorn | Latest | ASGI application server |

### Model Specifications
- **Name:** `all-MiniLM-L6-v2` (Hugging Face)
- **Size:** 133 MB (fast loading)
- **Dimensions:** 384-dimensional vectors
- **Performance:** 14.5× faster than BERT-base
- **Quality:** 96.3% of BERT-large accuracy

---

## 📁 Project Structure

```
materialmoversearch/
├── app/
│   ├── main.py                 # FastAPI app, routes, lifecycle
│   ├── core/
│   │   ├── config.py          # Settings & environment variables
│   │   └── database.py        # MongoDB connection & operations
│   ├── models/
│   │   └── schemas.py         # Pydantic request/response models
│   └── services/
│       ├── search.py          # Semantic search engine (BERT)
│       ├── keyword_search.py  # BM25 keyword search engine
│       └── hybrid_search.py   # Combines both engines
├── tests/
│   ├── test_memory.py         # Memory footprint analysis
│   ├── test_performance.py    # Response time distribution
│   └── test_throughput.py     # Throughput benchmarks
├── .env                        # Environment configuration
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project metadata & dependencies
├── README.md                  # This file
└── QUICK_START.md             # Detailed API guide

```

### Key Files

- **`app/main.py`** - FastAPI application, routes, middleware, startup/shutdown
- **`app/services/hybrid_search.py`** - Orchestrates both search engines with weighted scoring
- **`app/services/search.py`** - BERT embeddings, cosine similarity, vector operations
- **`app/services/keyword_search.py`** - BM25 ranking, inverted index building
- **`app/core/database.py`** - MongoDB CRUD, embedding persistence
- **`app/models/schemas.py`** - Pydantic validation for requests/responses

---

## 🧪 Testing & Benchmarks

Run comprehensive performance tests:

```bash
# Run all tests once
uv run python run_all_tests.py

# Run tests 3 times for average analysis
uv run python run_tests_3x_analysis.py

# Individual test modules
uv run python -m pytest tests/test_memory.py
uv run python -m pytest tests/test_performance.py
uv run python -m pytest tests/test_throughput.py
```

**Test Coverage:**
- ✅ Memory footprint & scalability
- ✅ Throughput by algorithm (semantic/keyword/hybrid)
- ✅ Response time distribution (p50, p90, p95, p99)
- ✅ Concurrent query simulation
- ✅ Index statistics & performance variance
