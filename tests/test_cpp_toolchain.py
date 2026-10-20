"""Compile and execute a tiny standard-library program, not an algorithm."""

from pathlib import Path
import subprocess

import pytest


@pytest.mark.cpp
def test_cpp_toolchain_compiles_and_executes(cpp_compile) -> None:
    source = Path(__file__).parent / "fixtures/toolchain_smoke.cpp"
    executable = cpp_compile(source)
    result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "Algorithm Atlas toolchain ready\n"


@pytest.mark.cpp
def test_cpp_fixture_rejects_output_outside_temporary_directory(cpp_compile) -> None:
    with pytest.raises(ValueError, match="plain filename"):
        cpp_compile(Path(__file__), output_name="../outside")
