"""Master test runner - run all performance tests"""
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.test_memory import test_memory_footprint
from tests.test_throughput import test_bm25_throughput, test_semantic_throughput, test_hybrid_throughput
from tests.test_performance import test_response_time_distribution, test_concurrent_query_simulation


def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE PERFORMANCE TEST SUITE")
    print("="*70)
    print("\nThis test suite will measure:")
    print("  • Memory footprint")
    print("  • BM25 throughput")
    print("  • Semantic search throughput")
    print("  • Hybrid search throughput")
    print("  • Response time distribution")
    print("  • Concurrent query simulation")
    print("\nStarting tests...\n")
    
    start_time = time.time()
    
    try:
        # Memory test
        print("\n[1/6] Running memory footprint test...")
        memory_results = test_memory_footprint()
        
        # Throughput tests
        print("\n[2/6] Running BM25 throughput test...")
        bm25_results = test_bm25_throughput()
        
        print("\n[3/6] Running semantic search throughput test...")
        semantic_results = test_semantic_throughput()
        
        print("\n[4/6] Running hybrid search throughput test...")
        hybrid_results = test_hybrid_throughput()
        
        # Performance tests
        print("\n[5/6] Running response time distribution test...")
        response_time_results = test_response_time_distribution()
        
        print("\n[6/6] Running concurrent query simulation test...")
        concurrent_results = test_concurrent_query_simulation()
        
        # Final summary
        elapsed_time = time.time() - start_time
        
        print("\n\n" + "="*70)
        print("COMPREHENSIVE TEST SUMMARY REPORT")
        print("="*70)
        
        print(f"\nTotal test execution time: {elapsed_time:.2f} seconds")
        
        print(f"\n{'-'*70}")
        print("1. MEMORY FOOTPRINT")
        print(f"{'-'*70}")
        print(f"  Total memory used: {memory_results['final']:.2f} MB")
        print(f"  Memory for search engine: {memory_results['total_delta']:.2f} MB")
        print(f"  Total materials loaded: {memory_results['total_materials']}")
        print(f"  Memory per material: {memory_results['memory_per_material']*1024:.2f} KB")
        print(f"  Estimated for 10k materials: {memory_results['memory_per_material']*10000:.2f} MB")
        
        print(f"\n{'-'*70}")
        print("2. THROUGHPUT COMPARISON")
        print(f"{'-'*70}")
        print(f"  {'Algorithm':<20} {'Avg (ms)':<15} {'Min (ms)':<15} {'Max (ms)':<15} {'QPS':<15}")
        print(f"  {'-'*70}")
        print(f"  {'BM25':<20} {bm25_results['avg_time_ms']:<15.2f} {bm25_results['min_time']:<15.2f} {bm25_results['max_time']:<15.2f} {bm25_results['throughput_qps']:<15.2f}")
        print(f"  {'Semantic':<20} {semantic_results['avg_time_ms']:<15.2f} {semantic_results['min_time']:<15.2f} {semantic_results['max_time']:<15.2f} {semantic_results['throughput_qps']:<15.2f}")
        print(f"  {'Hybrid':<20} {hybrid_results['avg_time_ms']:<15.2f} {hybrid_results['min_time']:<15.2f} {hybrid_results['max_time']:<15.2f} {hybrid_results['throughput_qps']:<15.2f}")
        
        print(f"\n{'-'*70}")
        print("3. RESPONSE TIME DISTRIBUTION (100 requests)")
        print(f"{'-'*70}")
        print(f"  Min:               {response_time_results['min']:.2f}ms")
        print(f"  Max:               {response_time_results['max']:.2f}ms")
        print(f"  Mean:              {response_time_results['mean']:.2f}ms")
        print(f"  Median (p50):      {response_time_results['median']:.2f}ms")
        print(f"  Std Dev:           {response_time_results['stdev']:.2f}ms")
        print(f"  p90:               {response_time_results['p90']:.2f}ms")
        print(f"  p95:               {response_time_results['p95']:.2f}ms")
        print(f"  p99:               {response_time_results['p99']:.2f}ms")
        
        print(f"\n{'-'*70}")
        print("4. CONCURRENT QUERY SIMULATION")
        print(f"{'-'*70}")
        print(f"  Total requests:    {concurrent_results['total_requests']}")
        print(f"  Average response:  {concurrent_results['avg_time']:.2f}ms")
        print(f"  Min response:      {concurrent_results['min_time']:.2f}ms")
        print(f"  Max response:      {concurrent_results['max_time']:.2f}ms")
        print(f"  Throughput:        {concurrent_results['throughput']:.2f} queries/second")
        
        print(f"\n{'-'*70}")
        print("PERFORMANCE VERDICT")
        print(f"{'-'*70}")
        
        # Performance analysis
        if hybrid_results['throughput_qps'] > 10:
            print(f"  ✅ Hybrid search throughput EXCELLENT ({hybrid_results['throughput_qps']:.2f} q/s)")
        elif hybrid_results['throughput_qps'] > 5:
            print(f"  ✅ Hybrid search throughput GOOD ({hybrid_results['throughput_qps']:.2f} q/s)")
        else:
            print(f"  ⚠️  Hybrid search throughput NEEDS OPTIMIZATION ({hybrid_results['throughput_qps']:.2f} q/s)")
        
        if response_time_results['mean'] < 50:
            print(f"  ✅ Response time EXCELLENT (avg {response_time_results['mean']:.2f}ms)")
        elif response_time_results['mean'] < 100:
            print(f"  ✅ Response time GOOD (avg {response_time_results['mean']:.2f}ms)")
        else:
            print(f"  ⚠️  Response time NEEDS OPTIMIZATION (avg {response_time_results['mean']:.2f}ms)")
        
        if memory_results['total_delta'] < 500:
            print(f"  ✅ Memory footprint EXCELLENT ({memory_results['total_delta']:.2f}MB)")
        elif memory_results['total_delta'] < 1000:
            print(f"  ✅ Memory footprint GOOD ({memory_results['total_delta']:.2f}MB)")
        else:
            print(f"  ⚠️  Memory footprint ACCEPTABLE ({memory_results['total_delta']:.2f}MB)")
        
        print(f"\n{'='*70}")
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
