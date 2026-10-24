"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def radii(text):
    _support.checked(text)
    n = len(text)
    odd,even = [0]*n,[0]*n
    left,right = 0,-1
    for i in range(n):
        k = 1 if i > right else min(odd[left+right-i],right-i+1)
        while i-k >= 0 and i+k < n and text[i-k] == text[i+k]:
            k += 1
        odd[i] = k
        if i+k-1 > right:
            left,right = i-k+1,i+k-1
    left,right = 0,-1
    for i in range(n):
        k = 0 if i > right else min(even[left+right-i+1],right-i+1)
        while i-k-1 >= 0 and i+k < n and text[i-k-1] == text[i+k]:
            k += 1
        even[i] = k
        if i+k-1 > right:
            left,right = i-k,i+k-1
    return odd,even


def solve(text):
    odd,even = radii(text)
    best = [0,0]
    for i in range(len(text)):
        for start,end in ((i-odd[i]+1,i+odd[i]),(i-even[i],i+even[i])):
            length = end-start
            if length > best[1]-best[0] or (length == best[1]-best[0] and start < best[0]):
                best = [start,end]
    return [odd,even,best]


if __name__ == "__main__":
    _support.main(solve, "palindrome")
