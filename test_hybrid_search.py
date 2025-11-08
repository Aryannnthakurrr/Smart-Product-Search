"""Test hybrid search API"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("HEALTH CHECK")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    print()

def test_search(query, semantic_weight=0.6, keyword_weight=0.4):
    """Test hybrid search"""
    print("=" * 60)
    print(f"HYBRID SEARCH: '{query}'")
    print(f"Weights: Semantic={semantic_weight}, Keyword={keyword_weight}")
    print("=" * 60)
    
    response = requests.get(
        f"{BASE_URL}/search",
        params={
            "query": query,
            "top_k": 5,
            "min_score": 0.1,
            "semantic_weight": semantic_weight,
            "keyword_weight": keyword_weight
        }
    )
    
    data = response.json()
    print(f"Query: {data['query']}")
    print(f"Total results: {data['total']}\n")
    
    for i, result in enumerate(data['results'], 1):
        print(f"{i}. {result['title']}")
        print(f"   Category: {result['category']}")
        print(f"   Price: ${result['price']:.2f}")
        print(f"   📊 Semantic: {result.get('semantic_score', 0):.4f} | "
              f"Keyword: {result.get('keyword_score', 0):.4f} | "
              f"Combined: {result.get('combined_score', 0):.4f}")
        print()

def main():
    print("\n🚀 Testing Hybrid Search API\n")
    
    # Test health
    try:
        test_health()
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
        return
    
    # Test 1: Balanced hybrid search
    try:
        test_search("cement for foundation", semantic_weight=0.6, keyword_weight=0.4)
    except Exception as e:
        print(f"❌ Search failed: {e}\n")
    
    # Test 2: More semantic weight
    try:
        test_search("waterproofing bathroom", semantic_weight=0.8, keyword_weight=0.2)
    except Exception as e:
        print(f"❌ Search failed: {e}\n")
    
    # Test 3: More keyword weight (exact matches)
    try:
        test_search("steel bars", semantic_weight=0.3, keyword_weight=0.7)
    except Exception as e:
        print(f"❌ Search failed: {e}\n")
    
    # Test 4: Equal weights
    try:
        test_search("paint exterior walls", semantic_weight=0.5, keyword_weight=0.5)
    except Exception as e:
        print(f"❌ Search failed: {e}\n")

if __name__ == "__main__":
    main()
