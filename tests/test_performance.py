"""Performance testing - response time distribution"""
import time
import statistics
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.hybrid_search import HybridSearchEngine


def test_response_time_distribution():
    """Test response time distribution for hybrid search"""
    print("\n" + "="*70)
    print("RESPONSE TIME DISTRIBUTION TEST")
    print("="*70)
    
    search_engine = HybridSearchEngine()
    search_engine.initialize()
    
    query = "cement"
    num_requests = 100
    
    times = []
    
    print(f"\nRunning {num_requests} identical queries for '{query}'...")
    print(f"Progress: ", end="", flush=True)
    
    for i in range(num_requests):
        start = time.time()
        results = search_engine.search(query, top_k=10, semantic_weight=0.6, keyword_weight=0.4)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        
        if (i + 1) % 10 == 0:
            print(".", end="", flush=True)
    
    print(" Done!")
    
    # Calculate statistics
    sorted_times = sorted(times)
    p50 = sorted_times[int(len(times) * 0.50)]
    p90 = sorted_times[int(len(times) * 0.90)]
    p95 = sorted_times[int(len(times) * 0.95)]
    p99 = sorted_times[int(len(times) * 0.99)]
    
    print(f"\n{'='*70}")
    print("RESPONSE TIME STATISTICS (in milliseconds)")
    print(f"{'='*70}")
    print(f"\nCount:             {len(times)}")
    print(f"Min:               {min(times):.2f}ms")
    print(f"Max:               {max(times):.2f}ms")
    print(f"Mean:              {statistics.mean(times):.2f}ms")
    print(f"Median (p50):      {statistics.median(times):.2f}ms")
    print(f"Std Dev:           {statistics.stdev(times):.2f}ms")
    print(f"\nPercentiles:")
    print(f"  p50 (median):    {p50:.2f}ms")
    print(f"  p90:             {p90:.2f}ms")
    print(f"  p95:             {p95:.2f}ms")
    print(f"  p99:             {p99:.2f}ms")
    
    # Latency categories
    under_10ms = sum(1 for t in times if t < 10)
    under_50ms = sum(1 for t in times if t < 50)
    under_100ms = sum(1 for t in times if t < 100)
    over_100ms = sum(1 for t in times if t >= 100)
    
    print(f"\nLatency Categories:")
    print(f"  < 10ms:          {under_10ms} ({under_10ms/len(times)*100:.1f}%)")
    print(f"  < 50ms:          {under_50ms} ({under_50ms/len(times)*100:.1f}%)")
    print(f"  < 100ms:         {under_100ms} ({under_100ms/len(times)*100:.1f}%)")
    print(f"  >= 100ms:        {over_100ms} ({over_100ms/len(times)*100:.1f}%)")
    
    search_engine.shutdown()
    
    return {
        'times': times,
        'min': min(times),
        'max': max(times),
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times),
        'p50': p50,
        'p90': p90,
        'p95': p95,
        'p99': p99
    }


def test_concurrent_query_simulation():
    """Simulate concurrent queries using sequential timing"""
    print("\n" + "="*70)
    print("CONCURRENT QUERY SIMULATION TEST")
    print("="*70)
    
    search_engine = HybridSearchEngine()
    search_engine.initialize()
    
    queries = [
        "cement",
        "steel",
        "concrete",
        "sand",
        "gravel",
        "bricks",
        "tiles",
        "paint"
    ]
    
    # Simulate 50 sequential requests with 8 different queries
    num_rounds = 50 // len(queries)
    times = []
    
    print(f"\nSimulating {len(queries) * num_rounds} sequential requests")
    print(f"(8 different queries, {num_rounds} rounds each)\n")
    print(f"Progress: ", end="", flush=True)
    
    for round_num in range(num_rounds):
        for query in queries:
            start = time.time()
            results = search_engine.search(query, top_k=10)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        
        print(".", end="", flush=True)
    
    print(" Done!")
    
    avg_time = statistics.mean(times)
    throughput = len(times) / (sum(times) / 1000)
    
    print(f"\n{'='*70}")
    print("CONCURRENT SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Total requests: {len(times)}")
    print(f"Average response time: {avg_time:.2f}ms")
    print(f"Min response time: {min(times):.2f}ms")
    print(f"Max response time: {max(times):.2f}ms")
    print(f"Throughput: {throughput:.2f} queries/second")
    
    search_engine.shutdown()
    
    return {
        'total_requests': len(times),
        'avg_time': avg_time,
        'min_time': min(times),
        'max_time': max(times),
        'throughput': throughput
    }


if __name__ == "__main__":
    try:
        response_time_results = test_response_time_distribution()
        concurrent_results = test_concurrent_query_simulation()
        
        print("\n✅ Performance tests completed successfully")
    except Exception as e:
        print(f"\n❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
