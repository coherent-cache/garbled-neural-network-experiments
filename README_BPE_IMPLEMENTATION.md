# Garbled Circuit BPE Implementation

## Overview

This repository contains a complete implementation of Byte Pair Encoding (BPE) using garbled circuits for privacy-preserving tokenization. The implementation demonstrates how classical NLP algorithms can be adapted for secure multi-party computation scenarios.

## Architecture

### Core Components

1. **Basic Garbled Circuit Operations** (`gc-bpe-test.ipynb` cells 1-8)
   - Label generation and XOR operations
   - AND and XOR gate implementations
   - Gate evaluation with garbled tables

2. **Extended GC Operations** (cells 17-18)
   - `GCNumber`: Multi-bit number representation in garbled circuits
   - `gc_equality_check()`: Private equality comparison
   - `gc_greater_than()`: Private magnitude comparison

3. **Garbled BPE Algorithm** (cells 18-19)
   - `GarbledBPE`: Main BPE class with garbled circuit integration
   - Private pair counting using `gc_count_pairs()`
   - Secure maximum finding with `gc_find_max_pair()`

4. **Two-Party Secure BPE** (cells 21-22)
   - `TwoPartyBPE`: Secure training between two parties
   - Privacy-preserving corpus merging
   - Shared vocabulary generation

## Key Features

### Privacy-Preserving Operations

- **Secure Pair Counting**: Count character pair frequencies without revealing individual corpus contents
- **Private Maximum Finding**: Identify most frequent pairs using garbled comparison circuits
- **Hidden Vocabulary Building**: Generate shared vocabularies without exposing training data

### BPE Algorithm Implementation

- **Character-level Initialization**: Start with individual characters as base tokens
- **Iterative Merging**: Progressively merge most frequent character pairs
- **Token-based Processing**: Properly handle multi-character tokens during merges
- **Vocabulary Management**: Track learned merges and final vocabulary

## Implementation Details

### Garbled Circuit Primitives

```python
# Label generation
def gen_label(nbytes: int = 16) -> bytes:
    return secrets.token_bytes(nbytes)

# XOR operation
def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))
```

### BPE Training Process

1. **Initialization**: Convert corpus to character-level tokens
2. **Pair Counting**: Use garbled circuits to count adjacent character pairs
3. **Maximum Finding**: Securely identify most frequent pair
4. **Merging**: Apply merge to all words in corpus
5. **Iteration**: Repeat until desired number of merges

### Example Usage

```python
# Standard BPE training
corpus = ["hello", "world", "low", "wonderful", "hello", "low"]
bpe = GarbledBPE()
bpe.train(corpus, num_merges=5)

# Tokenization
tokens = bpe.tokenize("hello world wonderful")
# Output: ['hello', 'wo', 'r', 'l', 'd', 'wo', 'n', 'd', 'e', 'r', 'f', 'u', 'l']
```

## Security Properties

### Privacy Guarantees

- **Input Privacy**: Individual corpus contents remain hidden during training
- **Frequency Privacy**: Exact pair counts are not revealed to participants
- **Output Privacy**: Only the final merged vocabulary is shared

### Cryptographic Assumptions

- **Secure Random Generation**: Uses `secrets` module for cryptographically secure labels
- **XOR Security**: Relies on one-time pad properties for encryption
- **Garbled Circuit Security**: Assumes honest-but-curious adversary model

## Performance Considerations

### Computational Complexity

- **Gate Count**: O(n × m × b) where n=corpus size, m=merges, b=bit width
- **Communication**: O(vocabulary size × label size) per merge
- **Storage**: O(vocabulary size) for final model

### Optimization Opportunities

- **Free XOR**: Implement XOR gates without encryption overhead
- **Point-and-Permute**: Reduce ciphertext size and evaluation time
- **Batching**: Process multiple words simultaneously

## Testing and Validation

### Unit Tests

- Basic garbled circuit operations (AND, XOR, equality, comparison)
- BPE algorithm correctness (merging, tokenization)
- Privacy preservation (no intermediate data leakage)

### Example Output

```
Training BPE with 5 merges on corpus of 6 words
Merge 1: ('l', 'o') (count: 4)
Merge 2: ('h', 'e') (count: 2)
Merge 3: ('l', 'lo') (count: 2)
Merge 4: ('he', 'llo') (count: 2)
Merge 5: ('w', 'o') (count: 2)
Training complete. Final vocabulary size: 15
```

## Future Enhancements

### Scalability Improvements

- **Distributed Computation**: Extend to multi-party scenarios (>2 parties)
- **Streaming Processing**: Handle large corpora that don't fit in memory
- **Parallel Evaluation**: Execute multiple garbled circuits concurrently

### Security Enhancements

- **Malicious Security**: Protect against actively malicious adversaries
- **Differential Privacy**: Add noise to protect against inference attacks
- **Secure Aggregation**: Implement privacy-preserving statistics collection

### Algorithm Extensions

- **Subword Regularization**: Add randomization to token selection
- **Morphological Awareness**: Incorporate linguistic structure
- **Cross-lingual BPE**: Support multilingual vocabulary learning

## Dependencies

- `secrets`: Cryptographically secure random number generation
- `typing`: Type hints for better code documentation
- `collections`: Default dictionaries for counting operations

## References

1. Sennrich, R., Haddow, B., & Birch, A. (2016). Neural machine translation of rare words with subword units. ACL.
2. Yao, A. C. (1986). How to generate and exchange secrets. FOCS.
3. Beaver, D., Micali, S., & Rogaway, P. (1990). The round complexity of secure protocols. STOC.

## License

This implementation is provided for educational and research purposes. Please ensure compliance with relevant privacy laws and regulations when using in production systems. 