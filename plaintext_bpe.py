from typing import List, Tuple, Dict
from collections import defaultdict
import time


class PlaintextBPE:
    """Standard BPE implementation without privacy preservation."""

    def __init__(self, vocab_size: int = 1000):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.merges = []

    def get_word_tokens(self, word: str) -> List[str]:
        """Split word into character tokens."""
        return list(word)

    def get_pairs(self, word_tokens: List[str]) -> set:
        """Get all adjacent pairs in word tokens."""
        pairs = set()
        for i in range(len(word_tokens) - 1):
            pairs.add((word_tokens[i], word_tokens[i + 1]))
        return pairs

    def count_pairs(self, corpus_tokens: List[List[str]]) -> Dict[Tuple[str, str], int]:
        """Count pair frequencies directly."""
        pair_counts = defaultdict(int)

        for word_tokens in corpus_tokens:
            pairs = self.get_pairs(word_tokens)
            for pair in pairs:
                pair_counts[pair] += 1

        return dict(pair_counts)

    def find_max_pair(self, pair_counts: Dict[Tuple[str, str], int]) -> Tuple[str, str]:
        """Find the most frequent pair directly."""
        if not pair_counts:
            return None

        return max(pair_counts.items(), key=lambda x: x[1])[0]

    def apply_merge(self, word_tokens: List[str], pair: Tuple[str, str]) -> List[str]:
        """Apply a merge to a list of word tokens."""
        new_tokens = []
        i = 0
        while i < len(word_tokens):
            if (
                i < len(word_tokens) - 1
                and word_tokens[i] == pair[0]
                and word_tokens[i + 1] == pair[1]
            ):
                new_tokens.append(pair[0] + pair[1])
                i += 2
            else:
                new_tokens.append(word_tokens[i])
                i += 1
        return new_tokens

    def train(self, corpus: List[str], num_merges: int = 100):
        """Train BPE using standard algorithm."""
        print(
            f"Training plaintext BPE with {num_merges} merges on corpus of {len(corpus)} words"
        )

        # Initialize with character-level vocabulary and tokenize corpus
        vocab = set()
        corpus_tokens = []
        for word in corpus:
            word_tokens = self.get_word_tokens(word)
            corpus_tokens.append(word_tokens)
            vocab.update(word_tokens)

        for merge_step in range(num_merges):
            # Count pairs directly
            pair_counts = self.count_pairs(corpus_tokens)

            if not pair_counts:
                break

            # Find most frequent pair directly
            best_pair = self.find_max_pair(pair_counts)

            if best_pair is None:
                break

            print(
                f"Merge {merge_step + 1}: {best_pair} (count: {pair_counts[best_pair]})"
            )

            # Apply merge to all words in corpus
            new_corpus_tokens = []
            for word_tokens in corpus_tokens:
                new_tokens = self.apply_merge(word_tokens, best_pair)
                new_corpus_tokens.append(new_tokens)

            corpus_tokens = new_corpus_tokens
            self.merges.append(best_pair)
            vocab.add(best_pair[0] + best_pair[1])

        self.vocab = {token: i for i, token in enumerate(sorted(vocab))}
        print(f"Training complete. Final vocabulary size: {len(self.vocab)}")

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using learned BPE merges."""
        words = text.split()
        result = []

        for word in words:
            word_tokens = list(word)

            # Apply merges in order
            for merge_pair in self.merges:
                word_tokens = self.apply_merge(word_tokens, merge_pair)

            result.extend(word_tokens)

        return result


def test_plaintext_bpe():
    """Test the plaintext BPE implementation."""
    # Create sample corpus
    corpus = ["hello", "world", "low", "wonderful", "hello", "low"]

    # Initialize and train BPE
    bpe = PlaintextBPE()
    bpe.train(corpus, num_merges=10)

    # Test tokenization
    test_text = "hello world wonderful"
    tokens = bpe.tokenize(test_text)

    print(f"\nOriginal text: {test_text}")
    print(f"BPE tokens: {tokens}")
    print(f"\nVocabulary: {bpe.vocab}")
    print(f"Learned merges: {bpe.merges}")

    return bpe


if __name__ == "__main__":
    print("Testing Plaintext BPE Implementation")
    print("=" * 40)
    trained_bpe = test_plaintext_bpe()
