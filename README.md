# Construction Material Semantic Search API �️

A powerful semantic search API for construction materials powered by FastAPI and sentence transformers. Search for construction materials from MongoDB using natural language queries and get semantically relevant results.

## Features

- 🔍 **Semantic Search**: Find construction materials using natural language queries
- ⚡ **Fast Performance**: Cached embeddings for instant search results
- 🎯 **Accurate Results**: Powered by sentence-transformers
- 📊 **Relevance Scores**: Each result includes a similarity score
- 💾 **MongoDB Integration**: Real-time data from MongoDB Atlas
- 🔄 **RESTful API**: Simple HTTP endpoints for easy integration
- 📚 **Auto Documentation**: Interactive API docs at `/docs`
- 🌐 **CORS Enabled**: Ready for frontend integration

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd materialmoversearch
```

2. Install dependencies (using uv or pip):
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### Running the API

Start the server:
```bash
uvicorn api:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 🏠 Root
**GET /** - API information and available endpoints

### 🔍 Search Materials
**GET /search** - Search for construction materials using semantic similarity

Query Parameters:
- `query` (required): Natural language search query
- `top_k` (optional, default: 5): Number of results to return (1-50)
- `min_score` (optional, default: 0.0): Minimum similarity score (0-1)

Example:
```bash
curl "http://localhost:8000/search?query=cement%20for%20foundation&top_k=5"
```

**POST /search** - Same as GET but with JSON body

Request Body:
```json
{
  "query": "steel rods for reinforcement",
  "top_k": 10,
  "min_score": 0.3
}
```

Example:
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "waterproofing material for roof", "top_k": 5}'
```

### ❤️ Health Check
**GET /health** - Check API status and total materials indexed

Example:
```bash
curl "http://localhost:8000/health"
```

### 🔄 Rebuild Cache
**POST /rebuild-cache** - Rebuild embeddings cache (admin endpoint)

Use this if you update the materials data in MongoDB.

## Example Usage

### Using cURL

```bash
# Simple search
curl "http://localhost:8000/search?query=cement%20bags"

# Search with parameters
curl "http://localhost:8000/search?query=steel%20beams&top_k=10&min_score=0.3"

# POST request
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "paint for exterior walls", "top_k": 5}'
```

### Using Python

```python
import requests

# Search for materials
response = requests.get(
    "http://localhost:8000/search",
    params={
        "query": "cement for foundation work",
        "top_k": 5,
        "min_score": 0.2
    }
)

results = response.json()
print(f"Found {results['count']} materials:")
for material in results['results']:
    print(f"- {material['title']} (score: {material['similarity_score']}, price: ${material['price']})")
```

### Using JavaScript/Fetch

```javascript
// GET request
const response = await fetch(
  'http://localhost:8000/search?query=steel+rods&top_k=5'
);
const data = await response.json();
console.log(data.results);

// POST request
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'waterproofing for roof',
    top_k: 10
  })
});
const data = await response.json();
```

## Response Format

Successful search response:
```json
{
  "query": "cement for foundation",
  "results": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Portland Cement",
      "description": "High-quality cement for construction...",
      "price": 250.0,
      "quantity": 500,
      "category": "Cement",
      "image": "https://example.com/image.jpg",
      "similarity_score": 0.8532
    }
  ],
  "count": 1
}
```

## Example Queries

Try these natural language queries:
- "cement for foundation work"
- "steel rods for reinforcement"
- "waterproofing material for roof"
- "paint for exterior walls"
- "tiles for bathroom flooring"
- "sand for concrete mixing"
- "bricks for wall construction"
- "adhesive for tile installation"
- "plywood for furniture making"
- "metal pipes for plumbing"

## Architecture

### Components

1. **api.py**: FastAPI application with REST endpoints
2. **lib/semantic_search.py**: Core semantic search engine
3. **MongoDB Atlas**: Construction materials database
4. **cache/**: Cached embeddings for fast search

### How It Works

1. On first startup, the API connects to MongoDB Atlas
2. It fetches all construction materials from the database
3. It generates embeddings for all materials using sentence-transformers
4. Embeddings are cached to disk for fast subsequent startups
5. Search queries are embedded and compared using cosine similarity
6. Top matching materials are returned with similarity scores and details

### Model

Uses `all-MiniLM-L6-v2` from sentence-transformers:
- Fast and efficient
- Good balance of speed and accuracy
- 384-dimensional embeddings
- Works well for semantic search

## Development

### Project Structure

```
materialmoversearch/
├── api.py                  # Main FastAPI application
├── lib/
│   └── semantic_search.py  # Search engine implementation
├── .env                    # MongoDB connection credentials
├── cache/                  # Auto-generated embeddings cache
├── main.py                 # Info script (run for instructions)
├── pyproject.toml          # Dependencies
├── README.md               # Full documentation
└── QUICKSTART.md           # Quick start guide
```

### Updating Materials

Materials are stored in MongoDB Atlas. To update the search index after changing the database:

```bash
curl -X POST "http://localhost:8000/rebuild-cache"
```

This will fetch the latest materials from MongoDB and regenerate the embeddings.

### Configuration

You can customize the search engine by modifying `lib/semantic_search.py`:
- Change the model: `model_name` parameter
- Adjust cache location: `cache_dir` parameter
- Modify search parameters: `top_k`, `min_score`

## Production Deployment

### Using Docker (Recommended)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t material-search-api .
docker run -p 8000:8000 -e MONGODB_URI="your-connection-string" material-search-api
```

### Using Production ASGI Server

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

Set these for production (create a `.env` file):
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
MONGODB_DATABASE=product
MONGODB_COLLECTION=Material-Mover
CORS_ORIGINS=https://yourdomain.com
```

## Performance

- **First startup**: 30-60 seconds (fetches from MongoDB, builds embeddings cache)
- **Subsequent startups**: 1-2 seconds (loads from cache)
- **Search latency**: < 100ms for typical queries
- **Throughput**: ~100-500 requests/second (single worker)
- **Database**: ~1000 construction materials indexed

## Troubleshooting

### Cache Issues
If you encounter cache-related errors, delete the cache folder:
```bash
rm -rf cache/
```
The cache will be rebuilt on next startup.

### Memory Usage
The API loads all embeddings into memory. For very large databases (>100k materials), consider:
- Using a vector database (Pinecone, Weaviate, Qdrant)
- Implementing batch processing
- Increasing server RAM

### MongoDB Connection Issues
If you can't connect to MongoDB:
- Check your connection string in `.env`
- Verify network access in MongoDB Atlas (whitelist your IP)
- Ensure credentials are correct
- Test connection with MongoDB Compass

### Model Download
On first run, sentence-transformers downloads the model (~90MB). Ensure:
- Internet connection is available
- Sufficient disk space (~500MB)
- No firewall blocking HuggingFace downloads

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use in your projects!

## Support

For issues or questions:
- Open an issue on GitHub
- Check the interactive docs at `/docs`
- Review the examples in this README

---

Built with ❤️ using FastAPI and sentence-transformers
