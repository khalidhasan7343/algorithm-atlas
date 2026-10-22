"""Deterministic Huffman tree codes for byte alphabets, with encode/decode."""
from collections.abc import Mapping
import heapq
import json
import re
import sys

MAX_MESSAGE = 10000
MAX_BITS = 1000000


class HuffmanCodec:
    """Heap ties use (frequency, minimum subtree byte, creation index)."""

    def __init__(self, frequencies: Mapping[int, int]):
        if not isinstance(frequencies, Mapping) or len(frequencies) > 256:
            raise ValueError("a mapping of at most 256 byte symbols required")
        for symbol, frequency in frequencies.items():
            if type(symbol) is not int or not 0 <= symbol <= 255:
                raise ValueError("symbols must be integer bytes 0..255")
            if type(frequency) is not int or not 1 <= frequency <= 10**9:
                raise ValueError("frequencies must be integers in 1..10^9")
        self._frequencies = dict(frequencies)
        self._nodes = []
        heap = []
        for symbol in sorted(frequencies):
            index = len(self._nodes)
            self._nodes.append((symbol, None, None))
            heapq.heappush(heap, (frequencies[symbol], symbol, index))
        while len(heap) > 1:
            weight_left, minimum_left, left = heapq.heappop(heap)
            weight_right, minimum_right, right = heapq.heappop(heap)
            index = len(self._nodes)
            self._nodes.append((None, left, right))
            heapq.heappush(heap, (weight_left + weight_right,
                                  min(minimum_left, minimum_right), index))
        self._root = heap[0][2] if heap else None
        self._codes = {}

        def visit(index: int, prefix: str) -> None:
            symbol, left, right = self._nodes[index]
            if symbol is not None:
                self._codes[symbol] = prefix or "0"
            else:
                visit(left, prefix + "0")
                visit(right, prefix + "1")

        if self._root is not None:
            visit(self._root, "")

    @property
    def codes(self) -> dict[int, str]:
        """Return an owned copy; changing it cannot corrupt the decoder tree."""
        return dict(self._codes)

    def weighted_length(self) -> int:
        return sum(frequency * len(self._codes[symbol])
                   for symbol, frequency in self._frequencies.items())

    def encode(self, message: bytes) -> str:
        if not isinstance(message, bytes) or len(message) > MAX_MESSAGE:
            raise ValueError("at most 10000 message bytes required")
        chunks = []
        length = 0
        for symbol in message:
            if symbol not in self._codes:
                raise ValueError("message contains unknown symbol")
            chunk = self._codes[symbol]
            length += len(chunk)
            if length > MAX_BITS:
                raise ValueError("encoded bit limit exceeded")
            chunks.append(chunk)
        return "".join(chunks)

    def decode(self, bits: str) -> bytes:
        if not isinstance(bits, str) or len(bits) > MAX_BITS:
            raise ValueError("at most 1000000 bits required")
        if self._root is None:
            if bits:
                raise ValueError("nonempty stream with empty alphabet")
            return b""
        output = bytearray()
        node = self._root
        for bit in bits:
            if bit not in ("0", "1"):
                raise ValueError("nonbinary stream")
            if self._nodes[self._root][0] is not None:
                if bit != "0":
                    raise ValueError("single-symbol code accepts zero bits only")
            else:
                node = self._nodes[node][1 if bit == "0" else 2]
            symbol = self._nodes[node][0]
            if symbol is not None:
                output.append(symbol)
                if len(output) > MAX_MESSAGE:
                    raise ValueError("decoded message limit exceeded")
                node = self._root
        if node != self._root:
            raise ValueError("truncated codeword")
        return bytes(output)


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if any(not re.fullmatch(r"[+-]?[0-9]+", x) for x in tokens):
            raise ValueError("expected ASCII decimal integers")
        numbers = [int(x) for x in tokens]
        if not numbers or not 0 <= numbers[0] <= 256:
            raise ValueError("expected alphabet size 0..256")
        size = numbers[0]
        offset = 1 + 2*size
        if len(numbers) <= offset:
            raise ValueError("missing frequencies or message count")
        frequencies = {}
        for symbol, frequency in zip(numbers[1:offset:2], numbers[2:offset:2]):
            if symbol in frequencies:
                raise ValueError("duplicate symbol")
            frequencies[symbol] = frequency
        count = numbers[offset]
        if not 0 <= count <= MAX_MESSAGE or len(numbers) != offset + 1 + count:
            raise ValueError("invalid message count")
        message_values = numbers[offset+1:]
        if any(not 0 <= value <= 255 for value in message_values):
            raise ValueError("message bytes must be in 0..255")
        codec = HuffmanCodec(frequencies)
        bits = codec.encode(bytes(message_values))
        result = {"codes": [[s, c] for s, c in sorted(codec.codes.items())],
                  "bits": bits, "decoded": list(codec.decode(bits)),
                  "cost": codec.weighted_length()}
        print(json.dumps(result, separators=(",", ":")))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
