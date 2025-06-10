import time
import tracemalloc
from typing import List, Dict, Any
import random
import string

# Import all implementations
from plaintext_bpe import PlaintextBPE
from proper_gc_bpe import ProperGarbledBPE


def generate_corpus(num_words: int, word_length_range: tuple = (3, 12)) -> List[str]:
    """Generate a synthetic corpus for testing."""
    vocab_chars = string.ascii_lowercase
    corpus = []
    for _ in range(num_words):
        word_len = random.randint(*word_length_range)
        word = "".join(random.choices(vocab_chars, k=word_len))
        corpus.append(word)
    return corpus


def measure_implementation(
    implementation_class, corpus: List[str], num_merges: int, name: str
) -> Dict[str, Any]:
    """Measure performance of a BPE implementation."""
    print(f"Benchmarking {name}...")

    tracemalloc.start()
    bpe = implementation_class()

    # Suppress output for cleaner results
    import sys
    from io import StringIO

    old_stdout = sys.stdout
    sys.stdout = StringIO()

    training_start = time.perf_counter()
    try:
        bpe.train(corpus, num_merges=num_merges)
    finally:
        sys.stdout = old_stdout

    training_end = time.perf_counter()
    training_time = training_end - training_start

    current, peak = tracemalloc.get_traced_memory()
    training_memory = peak / 1024 / 1024
    tracemalloc.stop()

    # Quick tokenization test
    test_text = "hello world programming"
    inference_start = time.perf_counter()
    tokens = bpe.tokenize(test_text)
    inference_end = time.perf_counter()
    inference_time = inference_end - inference_start

    return {
        "name": name,
        "training_time": training_time,
        "inference_time": inference_time,
        "memory_usage_mb": training_memory,
        "vocab_size": len(bpe.vocab),
        "num_merges_learned": len(bpe.merges),
    }


def print_results(results_list: List[Dict]):
    """Print benchmark results."""
    print(
        f"\n{'Implementation':<30} {'Training (s)':<15} {'Memory (MB)':<12} {'Vocab Size':<12}"
    )
    print("-" * 75)

    baseline = results_list[0]
    for results in results_list:
        if results == baseline:
            overhead_str = "baseline"
        else:
            overhead = results["training_time"] / baseline["training_time"]
            overhead_str = f"({overhead:.1f}x)"

        print(
            f"{results['name']:<30} {results['training_time']:<15.3f} "
            f"{results['memory_usage_mb']:<12.2f} {results['vocab_size']:<12} {overhead_str}"
        )


def main():
    print("BPE Implementation Benchmark")
    print("=" * 50)

    # Generate larger corpus
    corpus = generate_corpus(500)
    print(f"Generated corpus: {len(corpus)} words")

    # Benchmark both implementations
    num_merges = 100

    implementations = [
        (PlaintextBPE, "Plaintext BPE"),
        (ProperGarbledBPE, "Garbled Circuit BPE"),
    ]

    results_list = []
    for impl_class, name in implementations:
        results = measure_implementation(impl_class, corpus, num_merges, name)
        results_list.append(results)

    print_results(results_list)

    # Summary
    if len(results_list) >= 2:
        gc_overhead = (
            results_list[1]["training_time"] / results_list[0]["training_time"]
        )
        print(f"\nGarbled Circuit Overhead: {gc_overhead:.1f}x")


if __name__ == "__main__":
    main()
