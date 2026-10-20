"""Shared pytest fixtures for infrastructure and future algorithm tests."""

from __future__ import annotations

import os
from pathlib import Path
import shlex
import shutil
import subprocess
from collections.abc import Callable

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("algorithm-atlas")
    group.addoption(
        "--cpp-standard",
        choices=("all", "c++17", "c++20"),
        default="all",
        help="C++ standard to test; all runs both C++17 and C++20 (default).",
    )
    group.addoption(
        "--require-cpp",
        action="store_true",
        help="Fail if no C++ compiler is available, instead of skipping C++ tests.",
    )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "cpp_standard" in metafunc.fixturenames:
        option = metafunc.config.getoption("--cpp-standard")
        standards = ("c++17", "c++20") if option == "all" else (option,)
        metafunc.parametrize("cpp_standard", standards)


@pytest.fixture(scope="session")
def cpp_compiler(pytestconfig: pytest.Config) -> tuple[str, ...]:
    """Honor CXX, otherwise find g++ or clang++; never invoke a shell."""
    configured = os.environ.get("CXX")
    command = shlex.split(configured) if configured else []
    if configured and (not command or not shutil.which(command[0])):
        pytest.fail(f"CXX does not identify an available compiler: {configured!r}")
    if not command:
        compiler = shutil.which("g++") or shutil.which("clang++")
        if compiler:
            command = [compiler]
    if not command:
        message = "C++ tests need g++ or clang++; install one or configure CXX."
        if pytestconfig.getoption("--require-cpp"):
            pytest.fail(message)
        pytest.skip(message)
    return tuple(command)


@pytest.fixture
def cpp_compile(
    cpp_compiler: tuple[str, ...], cpp_standard: str, tmp_path: Path
) -> Callable[..., Path]:
    """Compile a source file in a temporary directory and return its executable.

    Example: executable = cpp_compile(Path(__file__).parents[1] / "cpp/solution.cpp")
    Run it with subprocess.run([str(executable)], check=True, timeout=10).
    Tests using this fixture run under both standards unless --cpp-standard selects one.
    """

    def compile_source(
        source: Path, *, output_name: str = "program", extra_flags: tuple[str, ...] = ()
    ) -> Path:
        if Path(output_name).name != output_name or output_name in ("", ".", ".."):
            raise ValueError("output_name must be a plain filename")
        executable = tmp_path / output_name
        command = [
            *cpp_compiler,
            f"-std={cpp_standard}",
            "-Wall",
            "-Wextra",
            "-pedantic",
            *extra_flags,
            str(source.resolve()),
            "-o",
            str(executable),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode:
            pytest.fail(
                f"C++ compilation failed ({cpp_standard}):\n"
                f"{shlex.join(command)}\n{result.stdout}{result.stderr}"
            )
        return executable

    return compile_source
