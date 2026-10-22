"""Require all nine cross-algorithm relationships to remain executable."""
from pathlib import Path
import subprocess
import sys


def test_cross_algorithm_matrix():
    root=Path(__file__).resolve().parents[3]
    result=subprocess.run([sys.executable,'scripts/verify_graph_cross_algorithms.py','--through','5'],cwd=root,capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stdout+result.stderr
