"""Validated sorted two-pointer pair search with earliest index-pair ties."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location("atlas_window_support",Path(__file__).resolve().parents[2]/"support.py")
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def solve(values, target):
    _support.array(values)
    _support.integer(target,-2*10**9,2*10**9)
    if any(values[i]>values[i+1] for i in range(len(values)-1)):
        raise ValueError("values must be sorted nondecreasing")
    left,right=0,len(values)-1
    while left<right:
        total=values[left]+values[right]
        if total<target:
            left+=1
        elif total>target:
            right-=1
        else:
            while right>left+1 and values[right-1]==values[right]:
                right-=1
            return [left,right]
    return []


if __name__=="__main__":_support.main(solve)
