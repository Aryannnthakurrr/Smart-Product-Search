"""Throughput testing for the search engine"""
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.hybrid_search import HybridSearchEngine


def test_bm25_throughput():
    """Test BM25 search throughput"""
    print("\n" + "="*70)
    print("BM25 THROUGHPUT TEST")
    print("="*70)
    
    search_engine = HybridSearchEngine()
    search_engine.initialize()
    
    queries = [
        "cement",
        "steel rebar",
        "concrete blocks",
        "sand",
        "gravel",
        "bricks",
        "tiles",
        "paint",
        "glass",
        "wood",
        "marble",
        "granite",
        "plywood",
        "drywall",
        "insulation",
    ]
    
    total_time = 0
    total_results = 0
    times = []
    
    print(f"\nRunning {len(queries)} BM25 searches...\n")
    print(f"{'Query':<25} {'Results':<10} {'Time (ms)':<12}")
    print(f"{'-'*47}")
    
    for query in queries:
        start = time.time()
        results = search_engine.keyword_engine.search(query, top_k=10)
        elapsed = (time.time() - start) * 1000
        
        times.append(elapsed)
        total_time += elapsed
        total_results += len(results)
        
        print(f"{query:<25} {len(results):<10} {elapsed:<12.2f}")
    
    avg_time = total_time / len(queries)
    throughput = len(queries) / (total_time / 1000)
    
    print(f"{'-'*47}")
    print(f"\n{'='*70}")
    print("BM25 THROUGHPUT RESULTS")
    print(f"{'='*70}")
    print(f"Total queries: {len(queries)}")
    print(f"Average search time: {avg_time:.2f}ms")
    print(f"Min time: {min(times):.2f}ms")
    print(f"Max time: {max(times):.2f}ms")
    print(f"Throughput: {throughput:.2f} queries/second")
    print(f"Total results returned: {total_results}")
    print(f"Average results per query: {total_results / len(queries):.2f}")
    
    search_engine.shutdown()
    
    return {
        'avg_time_ms': avg_time,
        'throughput_qps': throughput,
        'total_results': total_results,
        'min_time': min(times),
        'max_time': max(times)
    }


def test_semantic_throughput():
    """Test semantic search throughput"""
    print("\n" + "="*70)
    print("SEMANTIC SEARCH THROUGHPUT TEST")
    print("="*70)
    
    search_engine = HybridSearchEngine()
    search_engine.initialize()
    
    queries = [
        "cement",
        "steel rebar",
        "concrete blocks",
        "sand",
        "gravel",
        "bricks",
        "tiles",
        "paint",
        "glass",
        "wood",
        "marble",
        "granite",
        "plywood",
        "drywall",
        "insulation",
    ]
    
    total_time = 0
    total_results = 0
    times = []
    
    print(f"\nRunning {len(queries)} semantic searches...\n")
    print(f"{'Query':<25} {'Results':<10} {'Time (ms)':<12}")
    print(f"{'-'*47}")
    
    for query in queries:
        start = time.time()
        results = search_engine.semantic_engine.search(query, top_k=10)
        elapsed = (time.time() - start) * 1000
        
        times.append(elapsed)
        total_time += elapsed
        total_results += len(results)
        
        print(f"{query:<25} {len(results):<10} {elapsed:<12.2f}")
    
    avg_time = total_time / len(queries)
    throughput = len(queries) / (total_time / 1000)
    
    print(f"{'-'*47}")
    print(f"\n{'='*70}")
    print("SEMANTIC THROUGHPUT RESULTS")
    print(f"{'='*70}")
    print(f"Total queries: {len(queries)}")
    print(f"Average search time: {avg_time:.2f}ms")
    print(f"Min time: {min(times):.2f}ms")
    print(f"Max time: {max(times):.2f}ms")
    print(f"Throughput: {throughput:.2f} queries/second")
    print(f"Total results returned: {total_results}")
    print(f"Average results per query: {total_results / len(queries):.2f}")
    
    search_engine.shutdown()
    
    return {
        'avg_time_ms': avg_time,
        'throughput_qps': throughput,
        'total_results': total_results,
        'min_time': min(times),
        'max_time': max(times)
    }


def test_hybrid_throughput():
    """Test hybrid search throughput"""
    print("\n" + "="*70)
    print("HYBRID SEARCH THROUGHPUT TEST")
    print("="*70)
    
    search_engine = HybridSearchEngine()
    search_engine.initialize()
    
    queries = [
        "cement",
        "steel rebar",
        "concrete blocks",
        "sand",
        "gravel",
        "bricks",
        "tiles",
        "paint",
        "glass",
        "wood",
        "marble",
        "granite",
        "plywood",
        "drywall",
        "insulation",
    ]
    
    total_time = 0
    total_results = 0
    times = []
    
    print(f"\nRunning {len(queries)} hybrid searches (semantic_weight=0.6, keyword_weight=0.4)...\n")
    print(f"{'Query':<25} {'Results':<10} {'Time (ms)':<12}")
    print(f"{'-'*47}")
    
    for query in queries:
        start = time.time()
        results = search_engine.search(query, top_k=10, semantic_weight=0.6, keyword_weight=0.4)
        elapsed = (time.time() - start) * 1000
        
        times.append(elapsed)
        total_time += elapsed
        total_results += len(results)
        
        print(f"{query:<25} {len(results):<10} {elapsed:<12.2f}")
    
    avg_time = total_time / len(queries)
    throughput = len(queries) / (total_time / 1000)
    
    print(f"{'-'*47}")
    print(f"\n{'='*70}")
    print("HYBRID THROUGHPUT RESULTS")
    print(f"{'='*70}")
    print(f"Total queries: {len(queries)}")
    print(f"Average search time: {avg_time:.2f}ms")
    print(f"Min time: {min(times):.2f}ms")
    print(f"Max time: {max(times):.2f}ms")
    print(f"Throughput: {throughput:.2f} queries/second")
    print(f"Total results returned: {total_results}")
    print(f"Average results per query: {total_results / len(queries):.2f}")
    
    search_engine.shutdown()
    
    return {
        'avg_time_ms': avg_time,
        'throughput_qps': throughput,
        'total_results': total_results,
        'min_time': min(times),
        'max_time': max(times)
    }


if __name__ == "__main__":
    try:
        bm25_results = test_bm25_throughput()
        semantic_results = test_semantic_throughput()
        hybrid_results = test_hybrid_throughput()
        
        print("\n" + "="*70)
        print("THROUGHPUT TEST SUMMARY")
        print("="*70)
        
        print(f"\n{'Algorithm':<20} {'Avg Time (ms)':<18} {'Throughput (q/s)':<18}")
        print(f"{'-'*56}")
        print(f"{'BM25':<20} {bm25_results['avg_time_ms']:<18.2f} {bm25_results['throughput_qps']:<18.2f}")
        print(f"{'Semantic':<20} {semantic_results['avg_time_ms']:<18.2f} {semantic_results['throughput_qps']:<18.2f}")
        print(f"{'Hybrid':<20} {hybrid_results['avg_time_ms']:<18.2f} {hybrid_results['throughput_qps']:<18.2f}")
        
        print("\n✅ Throughput tests completed successfully")
    except Exception as e:
        print(f"\n❌ Throughput test failed: {e}")
        import traceback
        traceback.print_exc()
