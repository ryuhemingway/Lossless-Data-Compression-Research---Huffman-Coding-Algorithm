"""
Generate empirical data for the Huffman coding report.

Produces:
  output/time_vs_size.csv      — encode / decode time versus input size
  output/compression_ratio.csv — compression ratio by symbol distribution
  output/sample_run.txt        — a traceable end-to-end example
"""

import csv
import math
import os
import random
import string
import time
from collections import Counter

from huffman_coding import (
    build_code_table,
    build_frequency_table,
    build_huffman_tree,
    compress,
    decompress,
)


# Helper: Shannon entropy


def shannon_entropy(text: str) -> float:
    """Compute the Shannon entropy H(X) = - Σ p(x) · log₂ p(x) in bits per symbol.

    Entropy is the theoretical lower bound on average codeword length — Huffman
    coding approaches it from above.
    """
    n = len(text)
    if n == 0:
        return 0.0
    counts = Counter(text)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        entropy -= p * math.log2(p)
    return entropy


# Trial 1: time versus input size


def run_time_trials() -> list[dict]:
    """Measure encode and decode wall-clock time for increasing input sizes.

    Uses random ASCII text at each size so the alphabet remains roughly
    constant (~62 symbols) while the total symbol count *m* grows.  This
    isolates the Θ(m) term of the complexity.
    """
    results = []
    sizes = [100, 500, 1_000, 5_000, 10_000, 50_000, 100_000]

    for size in sizes:
        # Generate random text of the given length.
        text = "".join(random.choices(string.ascii_letters + string.digits, k=size))

        # Measure encoding time.
        t0 = time.perf_counter()
        compressed = compress(text)
        t_enc = time.perf_counter() - t0

        # Measure decoding time.
        t0 = time.perf_counter()
        decompressed = decompress(compressed)
        t_dec = time.perf_counter() - t0

        # Correctness guard.
        assert decompressed == text

        # Compute derived metrics.
        freq = build_frequency_table(text)
        root = build_huffman_tree(freq)
        codes = build_code_table(root)
        avg_code_len = sum(len(codes[ch]) * f for ch, f in freq.items()) / size

        results.append(
            {
                "input_size": size,
                "distinct_symbols": len(freq),
                "encode_time_s": round(t_enc, 6),
                "decode_time_s": round(t_dec, 6),
                "compressed_bytes": len(compressed),
                "original_bytes": len(text.encode("utf-8")),
                "ratio": round(len(compressed) / max(len(text.encode("utf-8")), 1), 4),
                "avg_code_len_bits": round(avg_code_len, 4),
                "entropy": round(shannon_entropy(text), 4),
            }
        )
        print(
            f"  size={size:>7}  "
            f"enc={t_enc:.4f}s  dec={t_dec:.4f}s  "
            f"ratio={results[-1]['ratio']}"
        )

    return results


# Trial 2: compression ratio versus symbol distribution


def run_compression_trials() -> list[dict]:
    """Measure how compression ratio varies with the skew of the distribution.

    Scenarios range from perfectly uniform (high entropy, poor compression)
    to extremely skewed (low entropy, excellent compression).
    """
    results = []
    size = 10_000
    alphabet = string.ascii_lowercase  # 'a'–'z'

    # Each scenario is a (name, weight_dict) pair.  Zipf scenarios are
    # generated programmatically below and stored as (name, generated_text).
    weight_scenarios: list[tuple[str, dict[str, int]]] = [
        ("uniform", {c: 1 for c in alphabet}),
        ("two_chars_equal", {"a": 1, "b": 1}),
        ("two_chars_skewed", {"a": 9, "b": 1}),
        ("single_char", {"a": 1}),
    ]

    # Pre-generate Zipf-distributed strings (heavy-tail distribution).
    pre_gen: list[tuple[str, str]] = []
    for s in [1.0, 2.0]:
        freqs = [1.0 / (i**s) for i in range(1, 27)]
        total = sum(freqs)
        probs = [f / total for f in freqs]
        text = "".join(random.choices(alphabet, weights=probs, k=size))
        name = f"zipf_n=26_s={s}"
        pre_gen.append((name, text))

    for name, weights in weight_scenarios:
        chars = list(weights.keys())
        w = list(weights.values())
        text = "".join(random.choices(chars, weights=w, k=size))

        compressed = compress(text)
        freq = build_frequency_table(text)
        root = build_huffman_tree(freq)
        codes = build_code_table(root)
        avg_code_len = sum(len(codes[ch]) * f for ch, f in freq.items()) / size
        h = shannon_entropy(text)

        results.append(
            {
                "scenario": name,
                "input_size": size,
                "entropy": round(h, 4),
                "avg_code_len_bits": round(avg_code_len, 4),
                "original_bytes": len(text.encode("utf-8")),
                "compressed_bytes": len(compressed),
                "ratio": round(len(compressed) / max(len(text.encode("utf-8")), 1), 4),
                "savings_pct": round(
                    (1 - len(compressed) / max(len(text.encode("utf-8")), 1)) * 100,
                    2,
                ),
            }
        )
        print(
            f"  {name:>25s}  "
            f"entropy={h:.3f}  avg_cw={avg_code_len:.2f}  "
            f"savings={results[-1]['savings_pct']:.1f}%"
        )

    # Process the pre-generated Zipf strings.
    for name, text in pre_gen:
        compressed = compress(text)
        freq = build_frequency_table(text)
        root = build_huffman_tree(freq)
        codes = build_code_table(root)
        avg_code_len = sum(len(codes[ch]) * f for ch, f in freq.items()) / size
        h = shannon_entropy(text)

        results.append(
            {
                "scenario": name,
                "input_size": size,
                "entropy": round(h, 4),
                "avg_code_len_bits": round(avg_code_len, 4),
                "original_bytes": len(text.encode("utf-8")),
                "compressed_bytes": len(compressed),
                "ratio": round(len(compressed) / max(len(text.encode("utf-8")), 1), 4),
                "savings_pct": round(
                    (1 - len(compressed) / max(len(text.encode("utf-8")), 1)) * 100,
                    2,
                ),
            }
        )
        print(
            f"  {name:>25s}  "
            f"entropy={h:.3f}  avg_cw={avg_code_len:.2f}  "
            f"savings={results[-1]['savings_pct']:.1f}%"
        )

    return results


# Sample run: a traceable end-to-end example


def write_sample_run() -> str:
    """Produce a human-readable trace of a full compress / decompress cycle."""
    text = "this is an example of huffman coding"
    freq = build_frequency_table(text)
    root = build_huffman_tree(freq)
    codes = build_code_table(root)
    encoded = compress(text)
    decoded = decompress(encoded)

    lines = []
    lines.append("=" * 60)
    lines.append("SAMPLE HUFFMAN ENCODING RUN")
    lines.append("=" * 60)
    lines.append(f"\nOriginal text ({len(text)} chars):\n  {text}\n")
    lines.append("Frequency table:")
    for ch, f in sorted(freq.items(), key=lambda x: -x[1]):
        lines.append(f"  '{ch}' (U+{ord(ch):04X}): {f}")
    lines.append("\nHuffman code table:")
    for ch, code in sorted(codes.items(), key=lambda x: (len(x[1]), x[1])):
        lines.append(f"  '{ch}': {code}")
    avg = sum(len(codes[c]) * freq[c] for c in freq) / max(len(text), 1)
    lines.append(
        f"\nAverage code length: {avg:.3f} bits/char (fixed-width would be 8 bits/char)"
    )
    lines.append(f"Shannon entropy:     {shannon_entropy(text):.3f} bits")

    bit_str = "".join(codes[ch] for ch in text)
    lines.append(f"\nEncoded bit string ({len(bit_str)} bits):")
    lines.append(f"  {bit_str[:80]}{'...' if len(bit_str) > 80 else ''}")

    lines.append(f"\nCompressed  bytes: {len(encoded)}")
    lines.append(f"Original    bytes: {len(text.encode('utf-8'))}")
    lines.append(
        f"Compression ratio: {len(encoded) / max(len(text.encode('utf-8')), 1):.3f}"
    )

    lines.append(f"\nDecoded text matches original: {decoded == text}")
    lines.append(f"Decoded: {decoded}")

    return "\n".join(lines) + "\n"


# Entry point


def main():
    os.makedirs("output", exist_ok=True)

    print("=" * 60)
    print("EMPIRICAL ANALYSIS — TIME VS INPUT SIZE")
    print("=" * 60)
    time_data = run_time_trials()
    with open("output/time_vs_size.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=time_data[0].keys())
        writer.writeheader()
        writer.writerows(time_data)
    print(f"\nSaved output/time_vs_size.csv ({len(time_data)} rows)\n")

    print("=" * 60)
    print("EMPIRICAL ANALYSIS — COMPRESSION RATIO BY DISTRIBUTION")
    print("=" * 60)
    ratio_data = run_compression_trials()
    with open("output/compression_ratio.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ratio_data[0].keys())
        writer.writeheader()
        writer.writerows(ratio_data)
    print(f"\nSaved output/compression_ratio.csv ({len(ratio_data)} rows)\n")

    print("=" * 60)
    print("SAMPLE RUN")
    print("=" * 60)
    sample = write_sample_run()
    with open("output/sample_run.txt", "w") as f:
        f.write(sample)
    print(sample)
    print("Saved output/sample_run.txt")


if __name__ == "__main__":
    random.seed(42)
    main()
