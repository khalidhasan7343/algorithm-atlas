"""Space-optimized Fibonacci within the shared signed-64 output domain."""
import sys
import re


def fibonacci(n: int) -> int:
    """Return F(n), F(0)=0, F(1)=1; reject indices outside 0..92."""
    if type(n) is not int or n < 0:
        raise ValueError("index must be a nonnegative integer")
    if n > 92:
        raise OverflowError("F(n) exceeds signed 64-bit")
    if n == 0:
        return 0
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


def _parse(token: str) -> int:
    if not re.fullmatch(r"[+-]?[0-9]+", token):
        raise ValueError("expected ASCII decimal integer")
    return int(token)


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if len(tokens) != 1:
            raise ValueError("expected one index")
        print(fibonacci(_parse(tokens[0])))
    except (ValueError, OverflowError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
