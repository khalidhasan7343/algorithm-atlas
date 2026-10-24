"""sliding-window-maximum: canonical window implementation."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location("atlas_window_support",Path(__file__).resolve().parents[2]/"support.py")
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


from collections import deque


def solve(values, k):
    _support.array(values)
    _support.integer(k,0,10000)
    if not values:
        if k != 0:
            raise ValueError("empty input requires window size zero")
        return []
    if not 1<=k<=len(values):
        raise ValueError("window size must be in 1..n")
    queue = deque()
    result = []
    for index,value in enumerate(values):
        while queue and queue[0]<=index-k:
            queue.popleft()
        while queue and values[queue[-1]]<=value:
            queue.pop()
        queue.append(index)
        if index+1>=k:
            result.append(values[queue[0]])
    return result


if __name__=="__main__":_support.main(solve)
