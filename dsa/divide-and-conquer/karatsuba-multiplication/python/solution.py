"""Direct divide-and-conquer implementation with exact integer contracts."""
from collections.abc import Sequence
import json
import re
import sys


def karatsuba_multiplication(a: int, b: int) -> int:
    """Exact signed Karatsuba product; direct multiplication only for 16-bit leaves."""
    if type(a) is not int or type(b) is not int:
        raise TypeError("operands must be native ints")

    def multiply(x: int, y: int) -> int:
        if not x or not y:
            return 0
        width = max(x.bit_length(), y.bit_length())
        if width <= 16:
            return x * y
        half = width // 2
        xh, yh = x >> half, y >> half
        xl, yl = x - (xh << half), y - (yh << half)
        low = multiply(xl, yl)
        high = multiply(xh, yh)
        middle = multiply(xl + xh, yl + yh) - low - high
        return (high << (2 * half)) + (middle << half) + low

    product = multiply(abs(a), abs(b))
    return -product if (a < 0) != (b < 0) else product


def main() -> int:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    try:
        if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
            raise ValueError("expected ASCII signed decimal integers")
        numbers = [int(token) for token in tokens]
        if len(numbers) != 2:
            raise ValueError("exactly two operands required")
        result = str(karatsuba_multiplication(*numbers))
        print(json.dumps(result, separators=(",", ":")))
    except (ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
