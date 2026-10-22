"""Unit insertion/deletion/substitution Levenshtein distance on scalar values."""
import sys


def edit_distance(first: str, second: str) -> int:
    for text in (first, second):
        if not isinstance(text, str) or len(text) > 1000:
            raise ValueError("strings of at most 1000 code points required")
        if any(0xD800 <= ord(c) <= 0xDFFF for c in text):
            raise ValueError("surrogates are not Unicode scalar values")
    if len(first) < len(second):
        first, second = second, first
    previous = list(range(len(second) + 1))
    for i, left in enumerate(first, 1):
        current = [i]
        for j, right in enumerate(second, 1):
            current.append(min(previous[j] + 1, current[j-1] + 1,
                               previous[j-1] + (left != right)))
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
        print(edit_distance(*lines))
    except (ValueError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
