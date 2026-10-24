"""longest-substring-without-repeating-characters: canonical window implementation."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location("atlas_window_support",Path(__file__).resolve().parents[2]/"support.py")
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def solve(text):
    _support._string.checked(text)
    last = [-1]*256
    left = 0
    best = [0,0]
    for right,byte in enumerate(text):
        left = max(left,last[byte]+1)
        last[byte] = right
        if right+1-left>best[1]-best[0]:
            best = [left,right+1]
    return best


if __name__=="__main__":_support.main(solve,byte_text=True)
