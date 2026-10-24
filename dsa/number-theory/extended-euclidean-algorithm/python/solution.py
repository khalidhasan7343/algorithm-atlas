"""extended-euclidean-algorithm: bounded canonical implementation."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_number_support", Path(__file__).resolve().parents[2]/"support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def solve(a: int, b: int) -> list[int]:
    _support.operand(a)
    _support.operand(b)
    if a == 0 and b == 0:
        return [0,0,0]
    old_r,r = abs(a),abs(b)
    old_x,x,old_y,y = 1,0,0,1
    while r:
        quotient = old_r//r
        old_r,r = r,old_r-quotient*r
        old_x,x = x,old_x-quotient*x
        old_y,y = y,old_y-quotient*y
    return [old_r,-old_x if a < 0 else old_x,-old_y if b < 0 else old_y]


if __name__=="__main__":
    _support.main(solve,2)
