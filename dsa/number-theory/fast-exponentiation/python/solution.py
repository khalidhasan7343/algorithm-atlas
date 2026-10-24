"""fast-exponentiation: bounded canonical implementation."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_number_support", Path(__file__).resolve().parents[2]/"support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def _multiply(a, b):
    product = a*b
    if not _support.MIN64 <= product <= _support.MAX64:
        raise ValueError("power does not fit signed 64-bit result")
    return product


def solve(base: int, exponent: int) -> int:
    _support.operand(base)
    _support.bounded(exponent, 0, 10**9)
    result = 1
    while exponent:
        if exponent & 1:
            result = _multiply(result,base)
        exponent >>= 1
        if exponent:
            base = _multiply(base,base)
    return result


if __name__=="__main__":
    _support.main(solve,2)
