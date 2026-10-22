"""Linear maximum-subarray DP with deterministic nonempty-interval ties."""
import json
import re
import sys


def maximum_subarray(values: list[int]) -> tuple[int, int, int] | None:
    """Maximize sum, then minimize start, then end-exclusive; empty gives None."""
    if len(values) > 10000:
        raise ValueError("at most 10000 values required")
    if any(type(v) is not int or not -10**9 <= v <= 10**9 for v in values):
        raise ValueError("values must be integers in +/-10^9")
    best = None
    current_sum, current_start = 0, 0
    for index, value in enumerate(values):
        if index == 0 or current_sum < 0:
            current_sum, current_start = value, index
        else:
            current_sum += value
        candidate = (current_sum, current_start, index + 1)
        if best is None or (-candidate[0], *candidate[1:]) < (-best[0], *best[1:]):
            best = candidate
    return best


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if any(not re.fullmatch(r"[+-]?[0-9]+", x) for x in tokens):
            raise ValueError("expected ASCII decimal integers")
        numbers = [int(x) for x in tokens]
        if not numbers or not 0 <= numbers[0] <= 10000 or len(numbers) != numbers[0] + 1:
            raise ValueError("expected count followed by values")
        result = maximum_subarray(numbers[1:])
        print(json.dumps(None if result is None else [str(result[0]), *result[1:]],
                         separators=(",", ":")))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
