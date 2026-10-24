"""prime-factorization: bounded canonical implementation."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_number_support", Path(__file__).resolve().parents[2]/"support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def solve(value: int) -> list[list[int]]:
    _support.bounded(value, 1, 10**12)
    factors = []
    divisor = 2
    while divisor <= value//divisor:
        exponent = 0
        while value % divisor == 0:
            value //= divisor
            exponent += 1
        if exponent:
            factors.append([divisor,exponent])
        divisor = 3 if divisor == 2 else divisor+2
    if value > 1:
        factors.append([value,1])
    return factors


if __name__=="__main__":
    _support.main(solve,1)
