"""LCS length over Unicode scalar values, with a rolling DP row."""
import sys


def lcs_length(first: str, second: str) -> int:
    for text in (first, second):
        if not isinstance(text, str) or len(text) > 1000:
            raise ValueError("strings of at most 1000 code points required")
        if any(0xD800 <= ord(c) <= 0xDFFF for c in text):
            raise ValueError("surrogates are not Unicode scalar values")
    if len(first) < len(second):
        first, second = second, first
    previous = [0] * (len(second) + 1)
    for left in first:
        current = [0]
        for j, right in enumerate(second, 1):
            current.append(previous[j - 1] + 1 if left == right
                           else max(previous[j], current[j - 1]))
        previous = current
    return previous[-1]


if __name__ == "__main__":
    try:
        text = sys.stdin.buffer.read().decode("utf-8")
        if text.endswith("\n"):
            text = text[:-1]
        lines = [line[:-1] if line.endswith("\r") else line for line in text.split("\n")]
        if len(lines) != 2:
            raise ValueError("expected exactly two text lines")
        print(lcs_length(*lines))
    except (ValueError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
