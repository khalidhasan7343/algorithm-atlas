"""Minimum cuts into palindromes; quadratic preprocessing and prefix DP."""
import sys


def minimum_palindrome_cuts(text: str) -> int:
    if not isinstance(text, str) or len(text) > 1000:
        raise ValueError("a string of at most 1000 code points required")
    if any(0xD800 <= ord(c) <= 0xDFFF for c in text):
        raise ValueError("surrogates are not Unicode scalar values")
    n = len(text)
    palindrome = [[False] * n for _ in range(n)]
    for left in range(n-1, -1, -1):
        for right in range(left, n):
            palindrome[left][right] = text[left] == text[right] and (
                right - left < 2 or palindrome[left+1][right-1]
            )
    pieces = [0] + [n+1] * n
    for end in range(1, n+1):
        for start in range(end):
            if palindrome[start][end-1]:
                pieces[end] = min(pieces[end], pieces[start] + 1)
    return pieces[n] - 1 if n else 0


if __name__ == "__main__":
    try:
        text = sys.stdin.buffer.read().decode("utf-8")
        if not text:
            raise ValueError("expected one text line, use LF for empty text")
        if text.endswith("\n"):
            text = text[:-1]
        if "\n" in text:
            raise ValueError("expected exactly one text line")
        if text.endswith("\r"):
            text = text[:-1]
        print(minimum_palindrome_cuts(text))
    except (ValueError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
