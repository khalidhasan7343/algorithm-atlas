"""modular-exponentiation: bounded canonical implementation."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_number_support", Path(__file__).resolve().parents[2]/"support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def solve(base: int, exponent: int, modulus: int) -> int:
    _support.operand(base)
    _support.bounded(exponent, 0, 10**9)
    _support.bounded(modulus, 1, 1000000007)
    base %= modulus
    result = 1 % modulus
    while exponent:
        if exponent & 1:
            result = (result*base) % modulus
        exponent >>= 1
        if exponent:
            base = (base*base) % modulus
    return result


if __name__=="__main__":
    _support.main(solve,3)
