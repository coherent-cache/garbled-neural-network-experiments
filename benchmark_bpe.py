import time
import tracemalloc
import sys
from typing import List, Dict, Any
import random
import string

# Import both implementations
from plaintext_bpe import PlaintextBPE
from test_gc_bpe import GarbledBPE


def generate_corpus(
    num_words: int, word_length_range: tuple = (3, 12), vocab_chars: str = None
) -> List[str]:
    """Generate a synthetic corpus for testing."""
    if vocab_chars is None:
        vocab_chars = string.ascii_lowercase

    corpus = []
    for _ in range(num_words):
        word_len = random.randint(*word_length_range)
        word = "".join(random.choices(vocab_chars, k=word_len))
        corpus.append(word)

    return corpus


def measure_performance(
    implementation_class, corpus: List[str], num_merges: int, name: str
) -> Dict[str, Any]:
    """Measure training and inference performance of a BPE implementation."""
    print(f"\n{'='*50}")
    print(f"Benchmarking {name}")
    print(f"{'='*50}")

    # Start memory tracking
    tracemalloc.start()

    # Training phase
    bpe = implementation_class()

    print(f"Training on {len(corpus)} words with {num_merges} merges...")
    training_start = time.perf_counter()

    bpe.train(corpus, num_merges=num_merges)

    training_end = time.perf_counter()
    training_time = training_end - training_start

    # Get memory usage after training
    current, peak = tracemalloc.get_traced_memory()
    training_memory = peak / 1024 / 1024  # Convert to MB

    tracemalloc.stop()

    # Inference phase
    test_texts = [
        "hello world wonderful programming",
        "machine learning natural language processing",
        "implementation benchmark performance analysis",
    ]

    print(f"Testing tokenization...")
    inference_start = time.perf_counter()

    all_tokens = []
    for text in test_texts:
        tokens = bpe.tokenize(text)
        all_tokens.extend(tokens)

    inference_end = time.perf_counter()
    inference_time = inference_end - inference_start

    results = {
        "name": name,
        "training_time": training_time,
        "inference_time": inference_time,
        "memory_usage_mb": training_memory,
        "vocab_size": len(bpe.vocab),
        "num_merges_learned": len(bpe.merges),
        "sample_tokens": all_tokens[:10],  # First 10 tokens as sample
        "merges": bpe.merges[:5],  # First 5 merges as sample
    }

    return results, bpe


def compare_correctness(plaintext_bpe, gc_bpe, test_texts: List[str]) -> Dict[str, Any]:
    """Compare the correctness of both implementations."""
    print(f"\n{'='*50}")
    print("Correctness Comparison")
    print(f"{'='*50}")

    comparison = {
        "identical_vocabs": set(plaintext_bpe.vocab.keys()) == set(gc_bpe.vocab.keys()),
        "identical_merges": plaintext_bpe.merges == gc_bpe.merges,
        "tokenization_differences": [],
    }

    for text in test_texts:
        plaintext_tokens = plaintext_bpe.tokenize(text)
        gc_tokens = gc_bpe.tokenize(text)

        if plaintext_tokens != gc_tokens:
            comparison["tokenization_differences"].append(
                {
                    "text": text,
                    "plaintext": plaintext_tokens,
                    "garbled_circuit": gc_tokens,
                }
            )

    print(f"Vocabularies identical: {comparison['identical_vocabs']}")
    print(f"Merges identical: {comparison['identical_merges']}")
    print(f"Tokenization differences: {len(comparison['tokenization_differences'])}")

    if comparison["tokenization_differences"]:
        print("\nTokenization differences found:")
        for diff in comparison["tokenization_differences"]:
            print(f"  Text: {diff['text']}")
            print(f"  Plaintext: {diff['plaintext']}")
            print(f"  GC: {diff['garbled_circuit']}")

    return comparison


def print_performance_comparison(plaintext_results: Dict, gc_results: Dict):
    """Print a detailed performance comparison."""
    print(f"\n{'='*60}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*60}")

    print(f"{'Metric':<25} {'Plaintext':<15} {'Garbled Circuit':<18} {'Overhead':<12}")
    print(f"{'-'*70}")

    # Training time
    training_overhead = gc_results["training_time"] / plaintext_results["training_time"]
    print(
        f"{'Training Time (s)':<25} {plaintext_results['training_time']:<15.4f} "
        f"{gc_results['training_time']:<18.4f} {training_overhead:<12.2f}x"
    )

    # Inference time
    inference_overhead = (
        gc_results["inference_time"] / plaintext_results["inference_time"]
    )
    print(
        f"{'Inference Time (s)':<25} {plaintext_results['inference_time']:<15.4f} "
        f"{gc_results['inference_time']:<18.4f} {inference_overhead:<12.2f}x"
    )

    # Memory usage
    memory_overhead = (
        gc_results["memory_usage_mb"] / plaintext_results["memory_usage_mb"]
    )
    print(
        f"{'Memory Usage (MB)':<25} {plaintext_results['memory_usage_mb']:<15.2f} "
        f"{gc_results['memory_usage_mb']:<18.2f} {memory_overhead:<12.2f}x"
    )

    # Vocabulary size
    vocab_diff = gc_results["vocab_size"] - plaintext_results["vocab_size"]
    print(
        f"{'Vocabulary Size':<25} {plaintext_results['vocab_size']:<15} "
        f"{gc_results['vocab_size']:<18} {vocab_diff:+d}"
    )

    # Merges learned
    merge_diff = (
        gc_results["num_merges_learned"] - plaintext_results["num_merges_learned"]
    )
    print(
        f"{'Merges Learned':<25} {plaintext_results['num_merges_learned']:<15} "
        f"{gc_results['num_merges_learned']:<18} {merge_diff:+d}"
    )


def run_scaling_benchmark():
    """Test how performance scales with corpus size."""
    print(f"\n{'='*60}")
    print("SCALING BENCHMARK")
    print(f"{'='*60}")

    corpus_sizes = [50, 100, 200, 500]
    scaling_results = {"plaintext": [], "garbled_circuit": []}

    for size in corpus_sizes:
        print(f"\nTesting with corpus size: {size}")
        corpus = generate_corpus(size, word_length_range=(4, 8))

        # Test plaintext
        start_time = time.perf_counter()
        plaintext_bpe = PlaintextBPE()
        plaintext_bpe.train(corpus, num_merges=10)
        plaintext_time = time.perf_counter() - start_time

        # Test garbled circuit
        start_time = time.perf_counter()
        gc_bpe = GarbledBPE()
        gc_bpe.train(corpus, num_merges=10)
        gc_time = time.perf_counter() - start_time

        scaling_results["plaintext"].append((size, plaintext_time))
        scaling_results["garbled_circuit"].append((size, gc_time))

        overhead = gc_time / plaintext_time if plaintext_time > 0 else float("inf")
        print(
            f"  Plaintext: {plaintext_time:.4f}s, GC: {gc_time:.4f}s, Overhead: {overhead:.2f}x"
        )

    return scaling_results


def main():
    """Run comprehensive benchmarks."""
    print("BPE Implementation Benchmark Suite")
    print("=" * 60)

    # Generate test corpus
    print("Generating test corpus...")
    corpus = generate_corpus(100, word_length_range=(4, 10))
    print(f"Generated corpus with {len(corpus)} words")
    print(f"Sample words: {corpus[:10]}")

    # Benchmark both implementations
    num_merges = 15

    plaintext_results, plaintext_bpe = measure_performance(
        PlaintextBPE, corpus, num_merges, "Plaintext BPE"
    )

    gc_results, gc_bpe = measure_performance(
        GarbledBPE, corpus, num_merges, "Garbled Circuit BPE"
    )

    # Compare correctness
    test_texts = [
        "hello world programming",
        "machine learning algorithms",
        "performance benchmark analysis",
    ]

    correctness = compare_correctness(plaintext_bpe, gc_bpe, test_texts)

    # Print detailed comparison
    print_performance_comparison(plaintext_results, gc_results)

    # Privacy vs Performance analysis
    print(f"\n{'='*60}")
    print("PRIVACY vs PERFORMANCE TRADE-OFFS")
    print(f"{'='*60}")

    total_overhead = (gc_results["training_time"] + gc_results["inference_time"]) / (
        plaintext_results["training_time"] + plaintext_results["inference_time"]
    )

    print(f"Overall Performance Overhead: {total_overhead:.2f}x")
    print(f"Privacy Guarantee: Complete input privacy in GC version")
    print(f"Security Model: Honest-but-curious adversaries")
    print(
        f"Communication Overhead: ~{gc_results['memory_usage_mb']:.1f}MB for garbled circuits"
    )

    # Scaling benchmark
    scaling_results = run_scaling_benchmark()

    print(f"\n{'='*60}")
    print("SCALING ANALYSIS")
    print(f"{'='*60}")

    print(f"{'Corpus Size':<12} {'Plaintext (s)':<15} {'GC (s)':<12} {'Overhead':<10}")
    print(f"{'-'*50}")

    for (pt_size, pt_time), (gc_size, gc_time) in zip(
        scaling_results["plaintext"], scaling_results["garbled_circuit"]
    ):
        overhead = gc_time / pt_time if pt_time > 0 else float("inf")
        print(f"{pt_size:<12} {pt_time:<15.4f} {gc_time:<12.4f} {overhead:<10.2f}x")

    # Summary recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")

    print("Use Plaintext BPE when:")
    print("  • Privacy is not a concern")
    print("  • Maximum performance is required")
    print("  • Working with large corpora (>10K words)")
    print("  • Real-time applications")

    print("\nUse Garbled Circuit BPE when:")
    print("  • Privacy is critical")
    print("  • Multi-party computation is needed")
    print("  • Small to medium corpora (<1K words)")
    print("  • Research/prototyping scenarios")

    print(
        f"\nOptimal threshold: ~{total_overhead:.1f}x performance cost for complete privacy"
    )


if __name__ == "__main__":
    main()
