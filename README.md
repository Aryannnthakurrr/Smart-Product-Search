# Movie Semantic Search API 🎬

A powerful semantic search API for movies powered by FastAPI and sentence transformers. Search for movies using natural language queries and get semantically relevant results.

## Features

- 🔍 **Semantic Search**: Find movies using natural language queries
- ⚡ **Fast Performance**: Cached embeddings for instant search results
- 🎯 **Accurate Results**: Powered by sentence-transformers
- 📊 **Relevance Scores**: Each result includes a similarity score
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

### 🔍 Search Movies
**GET /search** - Search for movies using semantic similarity

Query Parameters:
- `query` (required): Natural language search query
- `top_k` (optional, default: 5): Number of results to return (1-50)
- `min_score` (optional, default: 0.0): Minimum similarity score (0-1)

Example:
```bash
curl "http://localhost:8000/search?query=action%20movie%20with%20explosions&top_k=5"
```

**POST /search** - Same as GET but with JSON body

Request Body:
```json
{
  "query": "romantic comedy set in new york",
  "top_k": 10,
  "min_score": 0.3
}
```

Example:
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "sci-fi thriller about time travel", "top_k": 5}'
```

### ❤️ Health Check
**GET /health** - Check API status and total movies indexed

Example:
```bash
curl "http://localhost:8000/health"
```

### 🔄 Rebuild Cache
**POST /rebuild-cache** - Rebuild embeddings cache (admin endpoint)

Use this if you update the movies data file.

## Example Usage

### Using cURL

```bash
# Simple search
curl "http://localhost:8000/search?query=romantic%20comedy"

# Search with parameters
curl "http://localhost:8000/search?query=action%20thriller&top_k=10&min_score=0.3"

# POST request
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "family friendly animated movie", "top_k": 5}'
```

### Using Python

```python
import requests

# Search for movies
response = requests.get(
    "http://localhost:8000/search",
    params={
        "query": "space adventure with aliens",
        "top_k": 5,
        "min_score": 0.2
    }
)

results = response.json()
print(f"Found {results['count']} movies:")
for movie in results['results']:
    print(f"- {movie['title']} (score: {movie['similarity_score']})")
```

### Using JavaScript/Fetch

```javascript
// GET request
const response = await fetch(
  'http://localhost:8000/search?query=action+movie&top_k=5'
);
const data = await response.json();
console.log(data.results);

// POST request
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'romantic comedy',
    top_k: 10
  })
});
const data = await response.json();
```

## Response Format

Successful search response:
```json
{
  "query": "action movie with explosions",
  "results": [
    {
      "id": 1,
      "title": "Movie Title",
      "description": "Movie description...",
      "similarity_score": 0.8532
    }
  ],
  "count": 1
}
```

## Example Queries

Try these natural language queries:
- "action movie with explosions"
- "romantic comedy set in new york"
- "sci-fi thriller about time travel"
- "family friendly animated adventure"
- "horror movie in a haunted house"
- "drama about family relationships"
- "comedy with mistaken identity"
- "thriller with plot twists"
- "movie about artificial intelligence"
- "adventure film set in jungle"

## Architecture

### Components

1. **api.py**: FastAPI application with REST endpoints
2. **lib/semantic_search.py**: Core semantic search engine
3. **data/movies.json**: Movie database
4. **cache/**: Cached embeddings for fast search

### How It Works

1. On first startup, the API loads the movie database
2. It generates embeddings for all movies using sentence-transformers
3. Embeddings are cached to disk for fast subsequent startups
4. Search queries are embedded and compared using cosine similarity
5. Top matching movies are returned with similarity scores

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
├── data/
│   └── movies.json         # Movie database (5,000 movies)
├── cache/                  # Auto-generated embeddings cache
├── main.py                 # Info script (run for instructions)
├── pyproject.toml          # Dependencies
├── README.md               # Full documentation
└── QUICKSTART.md           # Quick start guide
```

### Adding Movies

Edit `data/movies.json` and add new movies in the format:
```json
{
  "id": 123,
  "title": "Movie Title",
  "description": "Movie description..."
}
```

Then rebuild the cache:
```bash
curl -X POST "http://localhost:8000/rebuild-cache"
```

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
docker build -t movie-search-api .
docker run -p 8000:8000 movie-search-api
```

### Using Production ASGI Server

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

Set these for production:
```bash
export CORS_ORIGINS="https://yourdomain.com"
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

## Performance

- **First startup**: 30-60 seconds (builds embeddings cache)
- **Subsequent startups**: 1-2 seconds (loads from cache)
- **Search latency**: < 100ms for typical queries
- **Throughput**: ~100-500 requests/second (single worker)

## Troubleshooting

### Cache Issues
If you encounter cache-related errors, delete the cache folder:
```bash
rm -rf cache/
```
The cache will be rebuilt on next startup.

### Memory Usage
The API loads all embeddings into memory. For very large databases (>100k movies), consider:
- Using a vector database (Pinecone, Weaviate, Qdrant)
- Implementing batch processing
- Increasing server RAM

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
