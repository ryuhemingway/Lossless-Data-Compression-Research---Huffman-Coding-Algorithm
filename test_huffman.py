import os
import tempfile
import unittest

from huffman_coding import (
    HuffmanNode,
    build_code_table,
    build_frequency_table,
    build_huffman_tree,
    compress,
    compress_file,
    decompress,
    decompress_file,
    encode,
    decode,
    roundtrip,
)


# ---------------------------------------------------------------------------
# Node unit tests
# ---------------------------------------------------------------------------


class TestHuffmanNode(unittest.TestCase):
    """Verify the HuffmanNode helpers behave correctly."""

    def test_leaf_detection(self):
        """A leaf has no children; an internal node does."""
        leaf = HuffmanNode("a", 5)
        self.assertTrue(leaf.is_leaf())
        parent = HuffmanNode(None, 10, leaf, HuffmanNode("b", 5))
        self.assertFalse(parent.is_leaf())

    def test_comparison(self):
        """Nodes are ordered by frequency for the min-heap."""
        a = HuffmanNode("a", 3)
        b = HuffmanNode("b", 5)
        self.assertLess(a, b)
        self.assertGreater(b, a)


# ---------------------------------------------------------------------------
# Frequency table tests
# ---------------------------------------------------------------------------


class TestFrequencyTable(unittest.TestCase):
    """Test the character-counting function."""

    def test_empty_string(self):
        """An empty string produces an empty frequency table."""
        self.assertEqual(build_frequency_table(""), {})

    def test_single_char(self):
        """A string of repeated characters counts correctly."""
        self.assertEqual(build_frequency_table("aaa"), {"a": 3})

    def test_multiple_chars(self):
        """Mixed characters are counted independently."""
        self.assertEqual(
            build_frequency_table("aab"),
            {"a": 2, "b": 1},
        )


# ---------------------------------------------------------------------------
# Tree construction tests
# ---------------------------------------------------------------------------


class TestBuildTree(unittest.TestCase):
    """Test the Huffman tree builder."""

    def test_empty_table_raises(self):
        """Building a tree from an empty table should raise a clear error."""
        with self.assertRaises(ValueError):
            build_huffman_tree({})

    def test_single_symbol(self):
        """A single symbol produces a root that is itself the leaf."""
        root = build_huffman_tree({"a": 10})
        self.assertTrue(root.is_leaf())
        self.assertEqual(root.char, "a")

    def test_two_symbols(self):
        """Two symbols produce one internal node summing their frequencies."""
        root = build_huffman_tree({"a": 5, "b": 3})
        self.assertFalse(root.is_leaf())
        self.assertEqual(root.freq, 8)

    def test_freq_sum(self):
        """The root's frequency equals the sum of all leaf frequencies."""
        root = build_huffman_tree({"a": 5, "b": 2, "c": 1, "d": 1})
        self.assertEqual(root.freq, 9)


# ---------------------------------------------------------------------------
# Code table tests
# ---------------------------------------------------------------------------


class TestCodeTable(unittest.TestCase):
    """Test codeword generation and the prefix property."""

    def test_single_symbol(self):
        """A single symbol gets the empty codeword (no bits needed to distinguish it)."""
        root = build_huffman_tree({"a": 1})
        codes = build_code_table(root)
        self.assertEqual(codes, {"a": ""})

    def test_prefix_property(self):
        """No codeword is a prefix of any other codeword — essential for unique decoding."""
        freq = {"a": 10, "b": 5, "c": 2, "d": 1}
        root = build_huffman_tree(freq)
        codes = build_code_table(root)
        for sym, code in codes.items():
            for other_sym, other_code in codes.items():
                if sym != other_sym:
                    self.assertFalse(
                        code.startswith(other_code) and code != other_code,
                        f"'{code}' is a prefix of '{other_code}'",
                    )

    def test_frequent_shorter(self):
        """The more frequent symbol must receive a code no longer than the less frequent one."""
        freq = {"a": 100, "b": 1}
        root = build_huffman_tree(freq)
        codes = build_code_table(root)
        self.assertLessEqual(len(codes["a"]), len(codes["b"]))


# ---------------------------------------------------------------------------
# Encode / Decode roundtrip tests
# ---------------------------------------------------------------------------


class TestEncodeDecode(unittest.TestCase):
    """Verify that compressing then decompressing returns the original text."""

    def test_roundtrip_empty(self):
        """An empty string should survive the roundtrip."""
        self.assertTrue(roundtrip(""))

    def test_roundtrip_single_char(self):
        """A string of a single repeated character survives."""
        self.assertTrue(roundtrip("aaaaa"))

    def test_roundtrip_alphabet(self):
        """A standard English pangram-like sentence survives."""
        text = "the quick brown fox jumps over the lazy dog"
        self.assertTrue(roundtrip(text))

    def test_roundtrip_unicode(self):
        """Non-ASCII characters (accents, CJK) survive the roundtrip."""
        text = "héllo wörld! こんにちは"
        self.assertTrue(roundtrip(text))

    def test_roundtrip_repeated(self):
        """A large string with only a handful of distinct symbols survives."""
        text = "aaaaabbbbbcccccdddddeeeeefffff" * 50
        self.assertTrue(roundtrip(text))

    def test_roundtrip_large(self):
        """A 10 000-character random ASCII string survives the roundtrip."""
        import random
        import string

        random.seed(42)
        text = "".join(random.choices(string.ascii_letters + string.digits, k=10_000))
        self.assertTrue(roundtrip(text))

    def test_decode_mid_codeword_rejected(self):
        """A bit string that stops in the middle of a codeword must raise an error."""
        # Construct a deterministic tree where "1" leads to an internal node.
        # Tree: root -> (left: "a") (right: internal -> (left: "b") (right: "c"))
        # Codes: a="0", b="10", c="11"
        # Decoding just "1" should fail — reaches internal node, not a leaf.
        root = HuffmanNode(
            None,
            3,
            left=HuffmanNode("a", 1),
            right=HuffmanNode(
                None,
                2,
                left=HuffmanNode("b", 1),
                right=HuffmanNode("c", 1),
            ),
        )
        with self.assertRaises(ValueError):
            decode("1", root)


# ---------------------------------------------------------------------------
# Compression ratio tests
# ---------------------------------------------------------------------------


class TestCompressionRatio(unittest.TestCase):
    """Verify that Huffman coding actually reduces size for skewed distributions."""

    def test_compresses_skewed_freq(self):
        """A heavily skewed distribution (one char dominates) should compress well."""
        text = "a" * 1000 + "b" * 10
        compressed = compress(text)
        self.assertLess(len(compressed), len(text.encode("utf-8")))

    def test_uniform_stays_reasonable(self):
        """Even a uniform distribution should not explode in size beyond a small overhead."""
        text = "abcdefgh" * 100
        compressed = compress(text)
        original = len(text.encode("utf-8"))
        # The header (tree) adds a small constant overhead; allow up to 50%.
        self.assertLess(len(compressed), original * 1.5)


# ---------------------------------------------------------------------------
# File I/O tests
# ---------------------------------------------------------------------------


class TestFileCompression(unittest.TestCase):
    """End-to-end test: write a file, compress it, decompress, and compare."""

    def test_file_roundtrip(self):
        """Compressing and decompressing a temporary file returns identical content."""
        text = "Hello world! This is a test of Huffman file compression.\n" * 200

        # Write original text to a temp file.
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(text)
            txt_path = f.name

        compressed_path = txt_path + ".huff"
        decompressed_path = txt_path + ".decomp"

        try:
            # Compress and verify stats.
            stats = compress_file(txt_path, compressed_path)
            self.assertIn("original_bytes", stats)
            self.assertIn("compressed_bytes", stats)
            self.assertIn("ratio", stats)

            # Decompress and compare.
            result = decompress_file(compressed_path, decompressed_path)
            self.assertEqual(result, text)

            # Confirm the decompressed file on disk matches.
            with open(decompressed_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), text)
        finally:
            # Clean up temporary files.
            for p in [txt_path, compressed_path, decompressed_path]:
                if os.path.exists(p):
                    os.unlink(p)
if __name__ == "__main__":
    unittest.main()
