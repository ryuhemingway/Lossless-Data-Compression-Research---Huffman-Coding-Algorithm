import heapq
import os
import struct
from collections import Counter
from typing import Dict, Optional, Tuple


class HuffmanNode:
    """Node in a Huffman tree.

    Attributes:
        char: The symbol stored at this node (None for internal nodes).
        freq: Sum of frequencies in the subtree rooted here.
        left: Left child (adds a '0' to the path).
        right: Right child (adds a '1' to the path).
    """

    def __init__(
        self,
        char: Optional[str],
        freq: int,
        left: Optional["HuffmanNode"] = None,
        right: Optional["HuffmanNode"] = None,
    ):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        """Return True if this node is a leaf (no children)."""
        return self.left is None and self.right is None

    def __lt__(self, other: "HuffmanNode") -> bool:
        """Compare by frequency for the min-heap."""
        return self.freq < other.freq

    def __repr__(self) -> str:
        return f"HuffmanNode(char={self.char!r}, freq={self.freq})"


def build_frequency_table(text: str) -> Dict[str, int]:
    """Count how many times each distinct character appears in *text*."""
    return dict(Counter(text))


def build_huffman_tree(freq_table: Dict[str, int]) -> HuffmanNode:
    """Build a Huffman tree from a symbol-to-frequency mapping.

    Uses a binary min-heap (heapq).  At each iteration the two nodes with
    the smallest weights are merged under a new parent whose weight is their
    sum.  This repeats until a single root remains.

    Raises ValueError if *freq_table* is empty.
    """
    if not freq_table:
        raise ValueError("Frequency table must not be empty")

    # Initialise the heap with one leaf per symbol.
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)

    # Repeatedly merge the two lightest nodes.
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, parent)

    return heap[0]


def build_code_table(root: HuffmanNode) -> Dict[str, str]:
    """Walk the tree and return a dict mapping each symbol to its binary codeword.

    A left branch appends '0', a right branch appends '1'.
    """
    code_table: Dict[str, str] = {}

    def _walk(node: HuffmanNode, prefix: str) -> None:
        if node.is_leaf():
            code_table[node.char] = prefix
            return
        if node.left:
            _walk(node.left, prefix + "0")
        if node.right:
            _walk(node.right, prefix + "1")

    _walk(root, "")
    return code_table


def encode(text: str, code_table: Dict[str, str]) -> str:
    """Translate *text* into a binary string using the Huffman code table."""
    return "".join(code_table[ch] for ch in text)


def decode(bit_string: str, root: HuffmanNode) -> str:
    """Decode a binary string back into the original text.

    Walks from the root following '0' (left) and '1' (right) until a leaf is
    reached; the leaf's symbol is emitted and the walk restarts at the root.

    Raises ValueError if the bit string is malformed.
    """
    result: list[str] = []
    node = root
    for bit in bit_string:
        if bit == "0":
            node = node.left
        else:
            node = node.right

        if node is None:
            raise ValueError(f"Invalid bit sequence: reached null child at '{bit}'")

        if node.is_leaf():
            result.append(node.char)
            node = root

    if node is not root:
        raise ValueError("Bit string ended in the middle of a codeword")
    return "".join(result)


# ---------------------------------------------------------------------------
# Tree serialisation — used to embed the tree in compressed file headers.
# The format is a pre-order traversal: 'L' + char for leaves, 'I' + children
# for internal nodes.
# ---------------------------------------------------------------------------


def _serialize_tree(node: HuffmanNode) -> str:
    """Encode the tree as a compact pre-order traversal string."""
    if node.is_leaf():
        return f"L{node.char}"
    return f"I{_serialize_tree(node.left)}{_serialize_tree(node.right)}"


def _deserialize_tree(data: str) -> Tuple[HuffmanNode, int]:
    """Reconstruct a Huffman tree from a serialised pre-order string.

    Returns (root, num_characters_consumed_from_data).
    """

    def _parse(pos: int) -> Tuple[HuffmanNode, int]:
        if pos >= len(data):
            raise ValueError("Unexpected end of tree data")
        marker = data[pos]
        pos += 1
        if marker == "L":
            if pos >= len(data):
                raise ValueError("Expected character after leaf marker")
            return HuffmanNode(char=data[pos], freq=0), pos + 1
        else:  # 'I' — internal node
            left, pos = _parse(pos)
            right, pos = _parse(pos)
            return HuffmanNode(char=None, freq=0, left=left, right=right), pos

    return _parse(0)


# ---------------------------------------------------------------------------
# Bit ↔ byte conversion helpers.
# ---------------------------------------------------------------------------


def _bits_to_bytes(bit_string: str) -> Tuple[bytes, int]:
    """Pack a binary string into bytes, zero-padding the last byte.

    Returns (bytes, number_of_padding_bits).
    """
    padding = (8 - len(bit_string) % 8) % 8
    padded = bit_string + "0" * padding
    byte_array = bytearray()
    for i in range(0, len(padded), 8):
        byte_array.append(int(padded[i : i + 8], 2))
    return bytes(byte_array), padding


def _bytes_to_bits(data: bytes, padding: int) -> str:
    """Unpack bytes into a binary string, stripping padding bits from the end."""
    bits = "".join(f"{byte:08b}" for byte in data)
    if padding > 0:
        bits = bits[:-padding]
    return bits


# ---------------------------------------------------------------------------
# Public compress / decompress (string in → bytes out).
# ---------------------------------------------------------------------------

# Wire format:
#   [4B: padding] [4B: tree_len] [4B: original_len] [tree_len B: tree] [payload]
#
# original_len is stored because a single unique symbol receives the empty
# codeword, making the encoded bit string zero-length.  Without the original
# count the decoder cannot know how many characters to emit.


def compress(data: str) -> bytes:
    """Compress a string into a self-describing byte sequence."""
    if not data:
        return struct.pack(">III", 0, 0, 0)

    freq = build_frequency_table(data)
    root = build_huffman_tree(freq)
    code_table = build_code_table(root)
    encoded_bits = encode(data, code_table)
    encoded_bytes, padding = _bits_to_bytes(encoded_bits)

    tree_bytes = _serialize_tree(root).encode("utf-8")

    return (
        struct.pack(">III", padding, len(tree_bytes), len(data))
        + tree_bytes
        + encoded_bytes
    )


def decompress(compressed: bytes) -> str:
    """Decompress bytes produced by *compress* back into the original string."""
    if len(compressed) < 12:
        raise ValueError("Invalid compressed data: too short")

    padding, tree_len, original_len = struct.unpack(">III", compressed[:12])
    offset = 12

    if tree_len == 0:
        return ""

    tree_bytes = compressed[offset : offset + tree_len]
    offset += tree_len
    tree_str = tree_bytes.decode("utf-8")

    root, _ = _deserialize_tree(tree_str)

    payload = compressed[offset:]
    bit_string = _bytes_to_bits(payload, padding)

    decoded = decode(bit_string, root)

    # Pad with the root leaf symbol when the encoded bit string is empty
    # (happens exactly when the alphabet has a single symbol).
    if len(decoded) < original_len and root.is_leaf():
        decoded += root.char * (original_len - len(decoded))

    return decoded


# ---------------------------------------------------------------------------
# File-level convenience functions.
# ---------------------------------------------------------------------------


def compress_file(input_path: str, output_path: str) -> Dict:
    """Read a UTF-8 text file, compress it, write the result to *output_path*.

    Returns a dict with compression statistics.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = f.read()

    original_size = len(data.encode("utf-8"))
    compressed = compress(data)
    compressed_size = len(compressed)

    with open(output_path, "wb") as f:
        f.write(compressed)

    return {
        "original_bytes": original_size,
        "compressed_bytes": compressed_size,
        "ratio": compressed_size / original_size if original_size else 1.0,
        "savings_pct": (
            (1 - compressed_size / original_size) * 100 if original_size else 0
        ),
    }


def roundtrip(text: str) -> bool:
    """Return True iff decompress(compress(text)) == text."""
    return decompress(compress(text)) == text


def decompress_file(input_path: str, output_path: str) -> str:
    """Read a compressed file, write the decompressed text back, return it."""
    with open(input_path, "rb") as f:
        compressed = f.read()

    decompressed = decompress(compressed)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(decompressed)

    return decompressed
