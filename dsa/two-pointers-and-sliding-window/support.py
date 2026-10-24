"""Shared array contracts and existing String byte transport; no algorithms."""
import importlib.util
import json
from pathlib import Path
import re
import sys

_spec=importlib.util.spec_from_file_location("approved_string_transport",Path(__file__).parent.parent/"string-algorithms/string_support.py")
_string=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_string)


def integer(value,low=-10**9,high=10**9):
    if type(value) is not int or not low<=value<=high:
        raise ValueError("integer outside supported range")
    return value


def array(values):
    if not isinstance(values,(list,tuple)) or len(values)>10000:
        raise ValueError("expected list/tuple of at most 10000 values")
    for value in values:integer(value)


def main(solve,byte_text=False):
    try:
        tokens=sys.stdin.read().split()
        if byte_text:
            if len(tokens)!=1:raise ValueError("expected one hex string")
            result=solve(_string.decode(tokens[0]))
        else:
            if not 1<=len(tokens)<=10001 or any(len(t)>20 or re.fullmatch(r"[+-]?[0-9]+",t) is None for t in tokens):
                raise ValueError("expected scalar prefix and decimal values")
            numbers=[integer(int(t),-(2**63),2**63-1) for t in tokens]
            result=solve(numbers[1:],numbers[0])
        print(json.dumps(result,separators=(",",":")))
    except (ValueError,TypeError) as error:
        print(f"error: {error}",file=sys.stderr)
        raise SystemExit(2)
