"""Memory footprint testing for the search engine"""
import psutil
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.hybrid_search import HybridSearchEngine


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def test_memory_footprint():
    """Test memory usage of the search engine"""
    print("\n" + "="*70)
    print("MEMORY FOOTPRINT TEST")
    print("="*70)
    
    initial_memory = get_memory_usage()
    print(f"\nInitial memory: {initial_memory:.2f} MB")
    
    # Initialize search engine
    print("\nInitializing hybrid search engine...")
    search_engine = HybridSearchEngine()
    search_engine.initialize()
    
    after_init = get_memory_usage()
    print(f"After initialization: {after_init:.2f} MB")
    print(f"Memory used for initialization: {after_init - initial_memory:.2f} MB")
    
    # Check index sizes
    print(f"\n{'='*70}")
    print("INDEX STATISTICS")
    print(f"{'='*70}")
    
    print(f"\nBM25 Index:")
    print(f"  - Number of materials: {len(search_engine.keyword_engine.docmap)}")
    print(f"  - Inverted index size: {len(search_engine.keyword_engine.index)}")
    print(f"  - Term frequencies tracked: {len(search_engine.keyword_engine.term_frequencies)}")
    print(f"  - Average document length: {search_engine.keyword_engine._get_avg_doc_length():.2f} tokens")
    
    print(f"\nSemantic Search:")
    print(f"  - Number of materials: {len(search_engine.semantic_engine.materials)}")
    print(f"  - Embeddings loaded: {len(search_engine.semantic_engine.embeddings)}")
    embedding_dim = search_engine.semantic_engine.embeddings[0].shape[0] if len(search_engine.semantic_engine.embeddings) > 0 else 0
    print(f"  - Embedding dimension: {embedding_dim}")
    
    # Calculate memory per material
    total_materials = len(search_engine.semantic_engine.materials)
    memory_per_material = (after_init - initial_memory) / total_materials if total_materials > 0 else 0
    
    print(f"\n{'='*70}")
    print("MEMORY PER MATERIAL")
    print(f"{'='*70}")
    print(f"Memory per material: {memory_per_material:.4f} MB ({memory_per_material * 1024:.2f} KB)")
    print(f"For 1000 materials: {memory_per_material * 1000:.2f} MB")
    print(f"For 10000 materials: {memory_per_material * 10000:.2f} MB")
    
    final_memory = get_memory_usage()
    print(f"\n{'='*70}")
    print("FINAL MEMORY REPORT")
    print(f"{'='*70}")
    print(f"Initial memory: {initial_memory:.2f} MB")
    print(f"Final memory: {final_memory:.2f} MB")
    print(f"Total memory used: {final_memory - initial_memory:.2f} MB")
    
    # Shutdown
    search_engine.shutdown()
    
    return {
        'initial': initial_memory,
        'after_init': after_init,
        'final': final_memory,
        'total_delta': final_memory - initial_memory,
        'memory_per_material': memory_per_material,
        'total_materials': total_materials
    }


if __name__ == "__main__":
    try:
        results = test_memory_footprint()
        print("\n✅ Memory test completed successfully")
    except Exception as e:
        print(f"\n❌ Memory test failed: {e}")
        import traceback
        traceback.print_exc()
