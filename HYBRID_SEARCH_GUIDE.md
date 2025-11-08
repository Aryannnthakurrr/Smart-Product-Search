# 🎯 Hybrid Search Implementation - Complete!

## ✅ What Was Done

I've successfully integrated **BM25 keyword search** with your existing **semantic search** to create a powerful **hybrid search system** for your construction materials API.

---

## 📦 Files Created/Modified

### New Files Created:
1. **`app/services/keyword_search.py`** - BM25 keyword search engine adapted for MongoDB
2. **`app/services/hybrid_search.py`** - Combines semantic + keyword search with weighted scoring
3. **`test_hybrid_search.py`** - Test script to demonstrate hybrid search
4. **`download_nltk.py`** - Downloads required NLTK data
5. **`add_fields.py`** - Added phone_number and address fields (already run successfully)

### Modified Files:
1. **`app/main.py`** - Updated to use HybridSearchEngine instead of SemanticSearchEngine
2. **`app/models/schemas.py`** - Added HybridSearchRequest model and score fields
3. **`requirements.txt`** - Added `nltk>=3.8.1` dependency

---

## 🚀 How Hybrid Search Works

### 1. **Dual Search Engines**
- **Semantic Search**: BERT embeddings + cosine similarity (great for meaning/context)
- **Keyword Search**: BM25 ranking (great for exact terms/acronyms)

### 2. **Score Combination**
Both searches run in parallel, scores are normalized to [0,1], then combined using weighted average:

```python
combined_score = (semantic_weight × semantic_score) + (keyword_weight × keyword_score)
```

### 3. **Default Weights**
- Semantic: **60%** (0.6) - Prioritizes understanding context
- Keyword: **40%** (0.4) - Ensures exact term matches aren't missed

---

## 📡 Updated API Endpoints

### `GET /search` - Hybrid Search

**New Parameters:**
```
query: str              # Search query (required)
top_k: int = 5          # Number of results
min_score: float = 0.3  # Minimum combined score
semantic_weight: float = 0.6  # Weight for semantic (NEW!)
keyword_weight: float = 0.4   # Weight for keyword (NEW!)
```

**Example Request:**
```bash
curl "http://localhost:8000/search?query=cement%20foundation&top_k=5&semantic_weight=0.7&keyword_weight=0.3"
```

**Example Response:**
```json
{
  "query": "cement foundation",
  "results": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "title": "Portland Cement Type I",
      "category": "Cement",
      "price": 450.00,
      "phone_number": "+91 64653 83314",
      "address": "501, Industrial Area, Meerut, UP - 342058",
      "semantic_score": 0.8542,      // NEW!
      "keyword_score": 0.7891,       // NEW!
      "combined_score": 0.8291       // NEW!
    }
  ],
  "total": 1
}
```

### `POST /search` - Hybrid Search with JSON

**Request Body:**
```json
{
  "query": "waterproofing bathroom",
  "top_k": 5,
  "min_score": 0.3,
  "semantic_weight": 0.6,
  "keyword_weight": 0.4
}
```

### `POST /rebuild-cache` - Rebuild Both Indexes

Now rebuilds:
- ✅ Semantic embeddings (460 materials)
- ✅ BM25 keyword index (460 materials)

---

## 🎯 When to Use Different Weights

### High Semantic Weight (0.7-0.9)
**Use When:** Searching with natural language queries
```
"materials for building a strong foundation"
"what do I need for bathroom waterproofing"
"good paint for outside walls"
```

### Balanced (0.5-0.6)
**Use When:** General purpose searches (DEFAULT)
```
"cement for foundation"
"steel reinforcement"
"exterior paint"
```

### High Keyword Weight (0.7-0.9)
**Use When:** Searching for specific terms/brands/codes
```
"Portland Type I"
"TMT bars 12mm"
"Asian Paints"
"PVC pipes"
```

---

## 🏗️ Architecture

```
User Query → Hybrid Search Engine
                ├─→ Semantic Search (BERT + Cosine)
                │      └─→ Score: 0.85
                │
                └─→ Keyword Search (BM25)
                       └─→ Score: 0.72
                            ↓
                   Normalize & Combine
                            ↓
                   Combined Score: 0.80
                            ↓
                   Rank & Filter Results
```

---

## 📊 Benefits of Hybrid Search

| Feature | Semantic Only | Keyword Only | **Hybrid** |
|---------|--------------|--------------|------------|
| Understands synonyms | ✅ | ❌ | ✅ |
| Handles misspellings | ✅ | ❌ | ✅ |
| Exact term matching | ⚠️ | ✅ | ✅ |
| Acronym/code search | ❌ | ✅ | ✅ |
| Natural language | ✅ | ❌ | ✅ |
| Brand names | ⚠️ | ✅ | ✅ |
| Context awareness | ✅ | ❌ | ✅ |

---

## 🧪 Testing

### Start the Server:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Test with Curl:
```bash
# Basic search
curl "http://localhost:8000/search?query=cement"

# With custom weights (more semantic)
curl "http://localhost:8000/search?query=cement%20foundation&semantic_weight=0.8&keyword_weight=0.2"

# With custom weights (more keyword)
curl "http://localhost:8000/search?query=Portland&semantic_weight=0.3&keyword_weight=0.7"
```

### Test with Python:
```python
import requests

response = requests.get(
    "http://localhost:8000/search",
    params={
        "query": "cement for foundation",
        "top_k": 5,
        "semantic_weight": 0.6,
        "keyword_weight": 0.4
    }
)

for result in response.json()["results"]:
    print(f"{result['title']}")
    print(f"  Semantic: {result['semantic_score']:.4f}")
    print(f"  Keyword: {result['keyword_score']:.4f}")
    print(f"  Combined: {result['combined_score']:.4f}")
```

---

## 🔧 Maintenance

### Rebuild Indexes After Bulk Updates:
```bash
curl -X POST "http://localhost:8000/rebuild-cache"
```

This will:
1. Regenerate all BERT embeddings
2. Rebuild BM25 inverted index
3. Save to disk cache (`cache/` directory)

### Cache Files Created:
```
cache/
├── embeddings.pkl           # Semantic embeddings
├── bm25_index.pkl          # BM25 inverted index
├── bm25_docmap.pkl         # Document mapping
├── bm25_term_frequencies.pkl  # Term frequencies
└── bm25_doc_lengths.pkl    # Document lengths
```

---

## 🎓 Technical Details

### BM25 Formula:
```
BM25(q,d) = Σ IDF(qi) × (tf(qi,d) × (k1 + 1)) / (tf(qi,d) + k1 × (1 - b + b × |d| / avgdl))
```

Where:
- `qi` = query terms
- `d` = document
- `tf` = term frequency
- `k1 = 1.5` (tuning parameter)
- `b = 0.75` (length normalization)
- `avgdl` = average document length

### Normalization:
Both scores are min-max normalized before combining:
```python
normalized_score = (score - min) / (max - min)
```

---

## ✅ Summary

You now have a **production-ready hybrid search system** that:

✅ Combines semantic understanding with keyword precision  
✅ Works with your existing 460-material MongoDB database  
✅ Supports customizable search weights via API  
✅ Returns detailed scoring breakdowns  
✅ Includes new fields (phone_number, address)  
✅ Caches indexes for fast performance  
✅ Can be rebuilt on-demand  

**The search is more intelligent and flexible than pure semantic search alone!** 🎉
