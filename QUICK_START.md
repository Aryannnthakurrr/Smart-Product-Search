# Quick Start Guide - Hybrid Search

## 🚀 Start the Server

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Wait for:
```
✅ Loaded 460 materials with embeddings
✅ Loaded BM25 index with 460 materials
✅ Hybrid search engine ready!
```

## 📡 API Examples

### 1. Basic Search (Default weights: 60% semantic, 40% keyword)
```bash
curl "http://localhost:8000/search?query=cement%20foundation&top_k=5"
```

### 2. More Semantic (Better for natural language)
```bash
curl "http://localhost:8000/search?query=materials%20for%20waterproofing&semantic_weight=0.8&keyword_weight=0.2"
```

### 3. More Keyword (Better for exact terms/brands)
```bash
curl "http://localhost:8000/search?query=Portland%20Type%20I&semantic_weight=0.3&keyword_weight=0.7"
```

### 4. Health Check
```bash
curl "http://localhost:8000/health"
```

### 5. Rebuild Indexes (after data updates)
```bash
curl -X POST "http://localhost:8000/rebuild-cache"
```

## 🔍 Access Swagger UI

Open in browser: **http://localhost:8000/docs**

## 📊 Understanding Scores

Each result includes:
- **semantic_score**: How well the meaning matches (0-1)
- **keyword_score**: How well the words match (0-1)  
- **combined_score**: Weighted combination of both

Higher = better match!

## ⚙️ Weight Recommendations

| Search Type | Semantic | Keyword | Example |
|------------|----------|---------|---------|
| Natural language | 0.7-0.9 | 0.1-0.3 | "good paint for walls" |
| Balanced | 0.5-0.6 | 0.4-0.5 | "cement foundation" |
| Exact terms | 0.1-0.3 | 0.7-0.9 | "TMT bars 12mm" |

## 🐛 Troubleshooting

**Server won't start?**
- Check MongoDB connection in `.env`
- Ensure nltk is installed: `uv pip install nltk`

**No results?**
- Lower min_score: `&min_score=0.1`
- Check query spelling
- Try adjusting weights

**Cache issues?**
- Delete `cache/` directory
- Run `/rebuild-cache` endpoint
