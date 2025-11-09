# Quick Start Guide - API Reference & Examples

Complete reference for all endpoints with working examples.

---

## 🚀 Start the Server

```bash
# Using uv (recommended)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or standard uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Startup confirmation:**
```
✅ Loaded 465 materials with embeddings
✅ Ready! 465 materials indexed for semantic search
✅ Loaded BM25 index from MongoDB with 465 materials
✅ Hybrid search engine ready!
```

**Access:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📡 Search Endpoints

### 1. `/recommend` - Simple Product IDs

**Purpose:** Get top 10 recommended product IDs (clean endpoint for integrations)

**Default Settings:**
- Top K: 10 products
- Semantic: 70%, Keyword: 30%
- Min Score: 0.3

**Request:**
```bash
curl "http://localhost:8000/recommend?query=cement%20foundation"
```

**Python:**
```python
import requests

response = requests.get(
    "http://localhost:8000/recommend",
    params={"query": "cement foundation"}
)
product_ids = response.json()["product_ids"]
print(product_ids)
```

**Response:**
```json
{
  "product_ids": [
    "673dc3d47f2a2c3aae0c2345",
    "673dc3d47f2a2c3aae0c2346",
    "673dc3d47f2a2c3aae0c2347"
  ]
}
```

---

### 2. `/search` (GET) - Full Hybrid Search

**Purpose:** Get detailed results with semantic, keyword, and combined scores

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `query` | string | *required* | Search query (any natural language) |
| `top_k` | int | 5 | Number of results (1-50) |
| `min_score` | float | 0.3 | Minimum combined score (0.0-1.0) |
| `semantic_weight` | float | 0.6 | Weight for semantic score (0.0-1.0) |
| `keyword_weight` | float | 0.4 | Weight for keyword score (0.0-1.0) |

**Examples:**

**a) Default (Balanced 60% semantic, 40% keyword):**
```bash
curl "http://localhost:8000/search?query=cement%20foundation&top_k=5"
```

**b) Natural Language Query (80% semantic, 20% keyword):**
```bash
curl "http://localhost:8000/search?query=materials%20for%20waterproofing&semantic_weight=0.8&keyword_weight=0.2"
```

**c) Exact Brand/Part (30% semantic, 70% keyword):**
```bash
curl "http://localhost:8000/search?query=Portland%20Type%20I&semantic_weight=0.3&keyword_weight=0.7"
```

**Python - Default Search:**
```python
import requests

response = requests.get(
    "http://localhost:8000/search",
    params={
        "query": "cement foundation",
        "top_k": 5,
        "min_score": 0.3
    }
)

data = response.json()
for result in data["results"]:
    print(f"{result['title']}")
    print(f"  Semantic:  {result['semantic_score']:.4f}")
    print(f"  Keyword:   {result['keyword_score']:.4f}")
    print(f"  Combined:  {result['combined_score']:.4f}")
    print()
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
      "quantity": 150,
      "brand": "UltraCem",
      "phone_number": "+91 98765 43210",
      "address": "123, MG Road, Mumbai, Maharashtra - 400001",
      "semantic_score": 0.8542,
      "keyword_score": 0.7891,
      "combined_score": 0.8291
    }
  ],
  "total": 1
}
```

---

### 3. `/search` (POST) - JSON Request

**Purpose:** Same as GET but with JSON body (better for complex/production scenarios)

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "waterproofing materials",
    "top_k": 5,
    "min_score": 0.3,
    "semantic_weight": 0.7,
    "keyword_weight": 0.3
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "waterproofing materials",
        "top_k": 5,
        "semantic_weight": 0.7,
        "keyword_weight": 0.3
    }
)

results = response.json()["results"]
```

---

## 🔧 Admin Endpoints

### `/health` - System Status

**Purpose:** Check API health and material count

**Request:**
```bash
curl "http://localhost:8000/health"
```

**Python:**
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

**Response:**
```json
{
  "status": "healthy",
  "materials_loaded": 465,
  "model": "all-MiniLM-L6-v2"
}
```

---

### `/rebuild-cache` - Rebuild Indexes

**Purpose:** Rebuild semantic embeddings and BM25 index from MongoDB

**Request:**
```bash
curl -X POST "http://localhost:8000/rebuild-cache"
```

**When to use:**
- After modifying materials directly in MongoDB
- To regenerate embeddings with new model
- After data cleanup/migration

---

### `/webhooks/product-created` - New Product

**Purpose:** Generate embedding for newly created product

**Parameters:** `product_id` (MongoDB ObjectId)

```bash
curl -X POST "http://localhost:8000/webhooks/product-created?product_id=673dc3d47f2a2c3aae0c2345"
```

---

### `/webhooks/product-updated` - Update Product

**Purpose:** Update embedding for modified product

**Parameters:** `product_id` (MongoDB ObjectId)

```bash
curl -X POST "http://localhost:8000/webhooks/product-updated?product_id=673dc3d47f2a2c3aae0c2345"
```

---

## 💡 Weight Selection Guide

Choose weights based on query type:

### Natural Language Queries (70-90% Semantic)
**Use when:** Query uses descriptive language, multiple words, meaning-based

**Example:** "materials for waterproofing exterior walls"
```bash
curl "http://localhost:8000/search?query=materials%20for%20waterproofing&semantic_weight=0.8&keyword_weight=0.2"
```

### Balanced Search (60% Semantic, 40% Keyword) - **DEFAULT**
**Use when:** General purpose, unsure of query type, mixed queries

**Example:** "cement for foundation"
```bash
curl "http://localhost:8000/search?query=cement%20for%20foundation"
```

### Exact Terms/Brands (10-30% Semantic)
**Use when:** Searching for specific brands, product codes, exact terms

**Example:** "Portland Type I"
```bash
curl "http://localhost:8000/search?query=Portland%20Type%20I&semantic_weight=0.2&keyword_weight=0.8"
```

---

## 📊 Performance Reference

From comprehensive testing (3 runs, 465 materials):

| Metric | Performance |
|--------|-------------|
| Semantic Search | 14.56 ms avg, 69.94 QPS |
| BM25 Keyword | 25.25 ms avg, 39.62 QPS |
| Hybrid Search | 46.95 ms avg, 21.37 QPS |
| **Concurrent Simulation** | **43.48 ms avg, 23.7 QPS** |
| **Response Time p99** | **70.90 ms** |
| **Memory per Material** | **91.88 KB** |

**Result:** 97% of requests < 50ms, 99% < 100ms ✅

---

## 🔍 Common Query Examples

| Intent | Query | Recommended Weights |
|--------|-------|-------------------|
| Find waterproofing | "waterproofing materials" | 0.8 / 0.2 |
| Specific product | "Portland Cement Type I" | 0.2 / 0.8 |
| Construction needs | "materials for strong foundation" | 0.7 / 0.3 |
| Category search | "roofing materials" | 0.6 / 0.4 (default) |
| Brand search | "Ambuja cement" | 0.3 / 0.7 |

---

## �️ Integration Examples

### JavaScript/Node.js
```javascript
const fetch = require('node-fetch');

// Simple recommendation
const recommendResponse = await fetch('http://localhost:8000/recommend?query=cement');
const ids = await recommendResponse.json();
console.log(ids.product_ids);

// Full search
const searchResponse = await fetch(
  'http://localhost:8000/search?query=cement&top_k=5&semantic_weight=0.6'
);
const results = await searchResponse.json();
console.log(results.results);
```

### PHP
```php
// Simple recommendation
$ch = curl_init('http://localhost:8000/recommend?query=cement');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
$data = json_decode($response, true);
print_r($data['product_ids']);
```

### cURL (Bash)
```bash
# Get product IDs
curl "http://localhost:8000/recommend?query=steel%20rods"

# Full search with custom weights
curl "http://localhost:8000/search?query=waterproofing&semantic_weight=0.8&top_k=3"

# Health check
curl "http://localhost:8000/health"
```

---

## ⚠️ Troubleshooting

**Q: Getting 500 errors on startup?**  
A: Check MongoDB connection in `.env` file. Run `curl http://localhost:8000/health` to verify.

**Q: Search returning empty results?**  
A: Try lowering `min_score` parameter (default 0.3). Check MongoDB has materials.

**Q: Slow first request?**  
A: Normal - first semantic search has model loading overhead (~150ms). Subsequent requests are fast.

**Q: How to handle real-time product updates?**  
A: Use `/webhooks/product-updated` endpoint when product data changes in MongoDB.

---

**Need more help?** Check `/docs` endpoint (Swagger UI) when server is running or see main `README.md`

### 5. `/rebuild-cache` - Rebuild Indexes

**Purpose:** Rebuild semantic embeddings and BM25 index after bulk data updates

**Request:**
```bash
curl -X POST "http://localhost:8000/rebuild-cache"
```

**Response:**
```json
{
  "status": "success",
  "message": "All embeddings and keyword index rebuilt",
  "semantic_materials": 460,
  "keyword_materials": 460
}
```

**When to Use:**
- After adding many new products
- After updating product descriptions
- If search results seem stale

---

## 🎯 Search Types Explained

### Semantic Search (BERT-based)
**Strengths:**
- ✅ Understands meaning and context
- ✅ Handles synonyms ("cement" = "concrete")
- ✅ Works with natural language
- ✅ Understands related concepts

**Best For:**
- "materials for building foundation"
- "what do I need for waterproofing"
- "strong concrete for construction"

**Weight Recommendation:** 0.7-0.9

---

### Keyword Search (BM25-based)
**Strengths:**
- ✅ Exact term matching
- ✅ Handles acronyms (TMT, PVC)
- ✅ Brand name precision
- ✅ Product codes

**Best For:**
- "Portland Type I"
- "TMT bars 12mm"
- "Asian Paints"
- "PVC pipes"

**Weight Recommendation:** 0.7-0.9

---

### Hybrid Search (Combined)
**Strengths:**
- ✅ Best of both worlds
- ✅ Balanced results
- ✅ Handles mixed queries
- ✅ Configurable per query

**Best For:**
- Most use cases
- General product search
- Unknown query types

**Weight Recommendation:** 0.5-0.6 (balanced)

---

## 💡 Weight Selection Guide

| Query Type | Example | Semantic | Keyword | Rationale |
|------------|---------|----------|---------|-----------|
| Natural Language | "good cement for foundations" | 0.8 | 0.2 | Understanding intent matters most |
| Descriptive | "waterproof material bathroom" | 0.7 | 0.3 | Mix of meaning + keywords |
| Balanced | "cement foundation" | 0.6 | 0.4 | Equal importance |
| Product Names | "Portland cement" | 0.4 | 0.6 | Exact term important |
| Brands/Codes | "Asian Paints exterior" | 0.3 | 0.7 | Exact matching crucial |
| SKU/Model | "TMT-12-500" | 0.1 | 0.9 | Must match exactly |

---

## 📊 Understanding Scores

Each result includes three scores:

**`semantic_score` (0.0 - 1.0)**
- Cosine similarity between query and product embeddings
- Higher = better semantic match
- Based on meaning/context

**`keyword_score` (0.0 - 1.0)**
- BM25 ranking score (normalized)
- Higher = better term frequency match
- Based on exact words

**`combined_score` (0.0 - 1.0)**
- Weighted combination of both
- `(semantic_weight × semantic_score) + (keyword_weight × keyword_score)`
- Final ranking score

---

## 🔍 Endpoint Comparison

| Feature | `/recommend` | `/search` |
|---------|-------------|-----------|
| **Returns** | Product IDs only | Full product details |
| **Response Size** | ~400 bytes | ~5-10 KB |
| **Customization** | Fixed optimal settings | Fully customizable |
| **Top K** | Fixed at 10 | 1-50 configurable |
| **Weights** | Fixed (0.7/0.3) | Adjustable per request |
| **Scores** | Not included | Semantic, keyword, combined |
| **Use Case** | Simple integration | Detailed search results |
| **Best For** | Product lists, widgets | Search pages, analysis |

---

## 🧪 Testing Examples

### Test All Search Types

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Simple recommendations
rec = requests.get(f"{BASE_URL}/recommend?query=cement").json()
print(f"Recommended: {len(rec['product_ids'])} products")

# 2. Semantic-heavy search
semantic = requests.get(
    f"{BASE_URL}/search",
    params={"query": "materials for waterproofing", "semantic_weight": 0.8}
).json()
print(f"Semantic results: {semantic['total']}")

# 3. Keyword-heavy search
keyword = requests.get(
    f"{BASE_URL}/search",
    params={"query": "Portland Type I", "keyword_weight": 0.8}
).json()
print(f"Keyword results: {keyword['total']}")

# 4. Balanced search
balanced = requests.get(
    f"{BASE_URL}/search",
    params={"query": "cement foundation"}
).json()
print(f"Balanced results: {balanced['total']}")
```

---

## 🐛 Troubleshooting

**Server won't start?**
- Check `.env` file has correct MongoDB URI
- Ensure `nltk` is installed: `uv pip install nltk`
- Check port 8000 is not in use

**No results returned?**
- Lower `min_score`: `&min_score=0.1`
- Check query spelling
- Try adjusting weights
- Verify products exist in database

**Slow searches?**
- Check MongoDB connection latency
- Ensure indexes are built (first run takes longer)
- Monitor memory usage
- Consider caching frequently searched terms

**Wrong results?**
- Adjust semantic/keyword weights
- Try POST with complex queries
- Check product descriptions in database
- Rebuild cache if data recently changed

---

## 🚀 Quick Integration

### React Example
```jsx
function ProductSearch() {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState([]);

  const search = async () => {
    const response = await fetch(
      `http://localhost:8000/recommend?query=${encodeURIComponent(query)}`
    );
    const data = await response.json();
    setProducts(data.product_ids);
  };

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={search}>Search</button>
      <ul>
        {products.map(id => <li key={id}>{id}</li>)}
      </ul>
    </div>
  );
}
```

### Node.js Example
```javascript
const axios = require('axios');

async function searchProducts(query) {
  const response = await axios.get('http://localhost:8000/search', {
    params: {
      query: query,
      top_k: 10,
      semantic_weight: 0.6,
      keyword_weight: 0.4
    }
  });
  return response.data.results;
}
```

---

For architecture details and advanced topics, see the main [README.md](README.md).
