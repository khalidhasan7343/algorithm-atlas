"""Validate the syllabus, canonical artifacts, statuses, and local Markdown links.

Planned/blocked records need an honest planning README, not implementation stubs.
This static check cannot establish that tests passed or verify external URLs; run
pytest and review test evidence before assigning a tested/reviewed status.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import html
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml


STATUSES = {"planned", "in-progress", "implemented", "tested", "reviewed", "blocked"}
ARTIFACT_STATUSES = {"implemented", "tested", "reviewed"}
STATUS_FIELDS = ("documentation_status", "python_status", "cpp_status", "test_status")
ALGORITHM_FIELDS = {
    "id", "name", "category", "canonical_location", "difficulty",
    *STATUS_FIELDS, "related_algorithms", "notes",
}
SECTIONS = (
    "Algorithm Name", "Overview", "Problem Statement", "Why Do We Need This Algorithm?",
    "Real-World Applications", "Core Intuition", "Prerequisites",
    "Step-by-Step Working Process", "Pseudocode", "Dry Run", "Time Complexity",
    "Space Complexity", "Python Implementation", "C++ Implementation",
    "Input and Output Examples", "Edge Cases", "Advantages",
    "Disadvantages and Limitations", "When to Use It", "When Not to Use It",
    "Comparison With Related Algorithms", "Interview Questions", "Practice Problems",
    "References", "Author Attribution",
)
IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "build", "dist",
}
KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SORTING_BATCHES = (
    ("bubble-sort", "selection-sort", "insertion-sort", "merge-sort"),
    ("quick-sort", "heap-sort", "counting-sort", "radix-sort"),
    ("bucket-sort", "shell-sort", "tim-sort"),
)
SEARCHING_BATCHES = (
    ("linear-search", "binary-search", "jump-search"),
    ("interpolation-search", "exponential-search", "ternary-search"),
)
RECURSION_BACKTRACKING_BATCHES = (
    ("permutations", "combinations", "power-set-generation"),
    ("n-queens", "sudoku-solver", "rat-in-a-maze"),
    ("graph-coloring", "hamiltonian-path", "subset-sum-backtracking"),
)
DYNAMIC_PROGRAMMING_SCOPE = "Dynamic Programming: eleven listed canonical topics only"
TREE_SCOPE = "Tree Algorithms category only"
STRING_SCOPE = "String Algorithms category only"
BIT_SCOPE = "Bit Manipulation category only"
NUMBER_WINDOW_SCOPE = "Number Theory and Two Pointers & Sliding Window categories only"
NUMBER_WINDOW_BATCHES = (
    ("sieve-of-eratosthenes", "euclidean-algorithm", "least-common-multiple"),
    ("modular-exponentiation", "fast-exponentiation", "extended-euclidean-algorithm", "prime-factorization"),
    ("two-sum-sorted-array",),
    ("sliding-window-maximum", "longest-substring-without-repeating-characters"),
)
BIT_BATCHES = (
    ("xor-unique-elements", "two-non-repeating-elements"),
    ("brian-kernighan-set-bit-counting", "subset-generation-bitmasking"),
)
STRING_BATCHES = (
    ("naive-pattern-matching", "knuth-morris-pratt", "rabin-karp"),
    ("z-algorithm", "boyer-moore", "manacher"),
    ("suffix-array", "suffix-tree", "aho-corasick"),
)
TREE_BATCHES = (
    ("inorder-traversal", "preorder-traversal", "postorder-traversal", "level-order-traversal"),
    ("lowest-common-ancestor", "binary-lifting", "euler-tour"),
    ("fenwick-tree", "segment-tree", "trie"),
    ("avl-tree-rotations", "red-black-tree-operations"),
    ("b-tree-operations", "b-plus-tree-operations"),
)
GRAPH_SCOPE = "Graph Algorithms category only"
GRAPH_BATCHES = (
    ("breadth-first-search", "depth-first-search", "union-find", "topological-sorting"),
    ("dijkstra", "bellman-ford", "floyd-warshall"),
    ("kruskal", "prim"),
    ("tarjan-strongly-connected-components", "kosaraju-strongly-connected-components", "bridges-detection", "articulation-points"),
    ("a-star-search", "johnson"),
)
GREEDY_SCOPE = "Greedy: four canonical topics only"
GREEDY_BATCHES = (
    ("activity-selection", "fractional-knapsack"),
    ("huffman-coding", "job-sequencing-with-deadlines"),
)
DYNAMIC_PROGRAMMING_BATCHES = (
    ("fibonacci", "zero-one-knapsack", "coin-change", "rod-cutting"),
    ("longest-common-subsequence", "longest-increasing-subsequence", "edit-distance"),
    ("matrix-chain-multiplication", "subset-sum", "palindrome-partitioning"),
    ("kadane",),
)


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate YAML mapping keys instead of silently overwriting them."""


def _unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode) -> dict:
    result: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise ValueError("YAML mapping keys must be scalar values") from exc
        if duplicate:
            raise ValueError(f"Duplicate YAML key: {key!r}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    categories: int = 0
    syllabus_entries: int = 0
    canonical_algorithms: int = 0
    markdown_files: int = 0
    local_links: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _relative_path(root: Path, value: Any) -> Path | None:
    if not _nonempty(value) or "\\" in value:
        return None
    parts = PurePosixPath(value)
    if parts.is_absolute() or str(parts) != value:
        return None
    if any(not KEBAB.fullmatch(part) for part in parts.parts):
        return None
    resolved = (root / value).resolve()
    return resolved if resolved.is_relative_to(root) else None


def _development_document(root: Path, value: Any) -> bool:
    """Accept a nonempty Markdown file through a safe repository-relative path."""
    if not _nonempty(value) or "\\" in value or re.match(r"^[A-Za-z]:", value):
        return False
    path = PurePosixPath(value)
    if (
        path.is_absolute() or str(path) != value or ".." in path.parts
        or path.suffix != ".md"
    ):
        return False
    try:
        resolved = (root / value).resolve()
        return (
            resolved.is_relative_to(root) and resolved.suffix == ".md"
            and resolved.is_file()
            and bool(resolved.read_text(encoding="utf-8").strip())
        )
    except (OSError, ValueError, RuntimeError, UnicodeError):
        return False


def _validate_development(
    root: Path, state: Any, algorithms: dict[str, dict], report: ValidationReport
) -> None:
    """Validate checkpoint claims statically, without claiming tests were run.

    Sorting and Searching enforce their approved batch memberships. Other
    future scopes share the state/path contract without inheriting those limits.
    """
    if not isinstance(state, dict):
        report.errors.append("development must be a mapping")
        return
    required = {
        "phase", "scope", "approval", "status", "active_batch",
        "completed_batches", "checkpoint",
    }
    if missing := sorted(required - state.keys()):
        report.errors.append(f"development is missing required fields: {', '.join(missing)}")
    for field_name in ("phase", "scope", "approval"):
        if not _nonempty(state.get(field_name)):
            report.errors.append(f"development.{field_name} must be a nonempty string")
    status = state.get("status")
    if not isinstance(status, str) or status not in ("in-progress", "awaiting-review"):
        report.errors.append("development.status must be in-progress or awaiting-review")
    for field_name in ("checkpoint", "completion_report"):
        if (field_name == "checkpoint" or field_name in state) and not _development_document(
            root, state.get(field_name)
        ):
            report.errors.append(
                f"development.{field_name} must name a safe relative existing nonempty .md file"
            )

    completed = state.get("completed_batches")
    valid_completed = (
        isinstance(completed, list)
        and all(type(batch) is int and batch > 0 for batch in completed)
    )
    if not valid_completed or completed != list(range(1, len(completed) + 1)):
        report.errors.append("development.completed_batches must be a contiguous prefix [1, 2, ...]")
        valid_completed = False
    active = state.get("active_batch")
    if active is not None and (type(active) is not int or active < 1):
        report.errors.append("development.active_batch must be a positive integer or null")
    if valid_completed and status == "in-progress" and (
        type(active) is not int or active != len(completed) + 1
    ):
        report.errors.append("development.active_batch must be the next uncompleted batch")
    if status == "awaiting-review" and active is not None:
        report.errors.append("development.awaiting-review requires active_batch=null")

    if state.get("scope") == NUMBER_WINDOW_SCOPE and valid_completed:
        if len(completed) > 4:
            report.errors.append("development combined phases have only four stages")
        if status == "in-progress" and (type(active) is not int or active not in (1, 2, 3, 4)):
            report.errors.append("development combined active_batch must be 1..4")
        if status == "awaiting-review" and completed != [1, 2, 3, 4]:
            report.errors.append("development combined awaiting-review requires all four stages")
        for batch in completed[:4]:
            for algorithm_id in NUMBER_WINDOW_BATCHES[batch-1]:
                record = algorithms.get(algorithm_id, {})
                if not all(isinstance(record.get(field), str) and record[field] in ARTIFACT_STATUSES for field in STATUS_FIELDS[:3]) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(f"development combined requires completed/tested {algorithm_id}")
        reports = state.get("completion_reports")
        phases = state.get("phase_records")
        if not isinstance(reports, dict) or set(reports) != {"11", "12"}:
            report.errors.append("development combined requires separate completion_reports for 11 and 12")
            reports = {}
        if reports.get("11") == reports.get("12"):
            report.errors.append("development combined completion reports must be distinct")
        if not isinstance(phases, dict) or set(phases) != {"11", "12"}:
            report.errors.append("development combined requires independent phase_records for 11 and 12")
            phases = {}
        for key, category, offset in (("11", "A9", 0), ("12", "A10", 2)):
            phase = phases.get(key, {})
            if not isinstance(phase, dict):
                report.errors.append(f"development phase {key} must be a mapping")
                continue
            count = max(0, min(2, len(completed)-offset))
            expected_status = ("awaiting-review" if count == 2 else
                               "planned" if key == "12" and len(completed) < 2 else "in-progress")
            if (phase.get("phase_number") != int(key) or phase.get("category") != category
                    or phase.get("status") != expected_status
                    or phase.get("completed_batches") != list(range(1, count+1))
                    or phase.get("owner_approval") != "pending"):
                report.errors.append(f"development phase {key} has inconsistent independent status/approval")
            for field in ("checkpoint", "completion_report"):
                if not _development_document(root, phase.get(field)):
                    report.errors.append(f"development phase {key} requires safe nonempty {field}")
            if reports.get(key) != phase.get("completion_report"):
                report.errors.append(f"development phase {key} completion_report mismatch")
        if state.get("completion_report") != reports.get("11"):
            report.errors.append("development primary completion_report must resolve to Phase 11")
        return
    if state.get("scope") == BIT_SCOPE and valid_completed:
        if len(completed) > 2:
            report.errors.append("development Bit Manipulation has only two batches")
        if status == "in-progress" and (type(active) is not int or active not in (1, 2)):
            report.errors.append("development Bit Manipulation active_batch must be 1..2")
        if status == "awaiting-review" and completed != [1, 2]:
            report.errors.append("development Bit Manipulation awaiting-review requires both batches")
        for batch in completed[:2]:
            for algorithm_id in BIT_BATCHES[batch-1]:
                record = algorithms.get(algorithm_id, {})
                if not all(isinstance(record.get(field), str) and record[field] in ARTIFACT_STATUSES for field in STATUS_FIELDS[:3]) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(f"development Bit Manipulation requires completed/tested {algorithm_id}")
        return
    if state.get("scope") == STRING_SCOPE and valid_completed:
        if len(completed) > 3:
            report.errors.append("development String Algorithms has only three batches")
        if status == "in-progress" and (type(active) is not int or active not in (1, 2, 3)):
            report.errors.append("development String Algorithms active_batch must be 1..3")
        if status == "awaiting-review" and completed != [1, 2, 3]:
            report.errors.append("development String Algorithms awaiting-review requires all three batches")
        for batch in completed[:3]:
            for algorithm_id in STRING_BATCHES[batch-1]:
                record = algorithms.get(algorithm_id, {})
                if not all(isinstance(record.get(field), str) and record[field] in ARTIFACT_STATUSES for field in STATUS_FIELDS[:3]) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(f"development String Algorithms requires completed/tested {algorithm_id}")
        return
    if state.get("scope") == TREE_SCOPE and valid_completed:
        if len(completed) > len(TREE_BATCHES):
            report.errors.append("development Tree Algorithms has only five batches")
        if status == "in-progress" and (type(active) is not int or active not in range(1, 6)):
            report.errors.append("development Tree Algorithms active_batch must be 1..5")
        if status == "awaiting-review" and completed != [1, 2, 3, 4, 5]:
            report.errors.append("development Tree Algorithms awaiting-review requires all five batches")
        for batch in completed[:5]:
            for algorithm_id in TREE_BATCHES[batch-1]:
                record = algorithms.get(algorithm_id, {})
                if not all(isinstance(record.get(field), str) and record[field] in ARTIFACT_STATUSES for field in STATUS_FIELDS[:3]) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(f"development Tree Algorithms requires completed/tested {algorithm_id}")
        return
    if state.get("scope") == GRAPH_SCOPE and valid_completed:
        if len(completed) > len(GRAPH_BATCHES):
            report.errors.append("development Graph Algorithms has only five batches")
        if status == "in-progress" and (type(active) is not int or active not in range(1, 6)):
            report.errors.append("development Graph Algorithms active_batch must be 1..5")
        if status == "awaiting-review" and completed != [1, 2, 3, 4, 5]:
            report.errors.append("development Graph Algorithms awaiting-review requires all five batches")
        for batch in completed[:5]:
            for algorithm_id in GRAPH_BATCHES[batch-1]:
                record = algorithms.get(algorithm_id, {})
                if not all(isinstance(record.get(field), str) and record[field] in ARTIFACT_STATUSES for field in STATUS_FIELDS[:3]) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(f"development Graph Algorithms requires completed/tested {algorithm_id}")
        return
    if state.get("scope") == GREEDY_SCOPE and valid_completed:
        if len(completed) > 2:
            report.errors.append("development Greedy has only two batches")
        if status == "in-progress" and (type(active) is not int or active not in (1, 2)):
            report.errors.append("development Greedy active_batch must be 1 or 2")
        if status == "awaiting-review" and completed != [1, 2]:
            report.errors.append("development Greedy awaiting-review requires both batches")
        for batch in completed[:2]:
            for algorithm_id in GREEDY_BATCHES[batch-1]:
                record = algorithms.get(algorithm_id, {})
                if not all(isinstance(record.get(field), str) and record[field] in ARTIFACT_STATUSES for field in STATUS_FIELDS[:3]) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(f"development Greedy requires completed/tested {algorithm_id}")
        return
    if state.get("scope") == DYNAMIC_PROGRAMMING_SCOPE and valid_completed:
        if len(completed) > 4:
            report.errors.append("development Dynamic Programming has only four batches")
        if status == "in-progress" and (type(active) is not int or active not in (1, 2, 3, 4)):
            report.errors.append("development Dynamic Programming active_batch must be 1..4")
        if status == "awaiting-review" and completed != [1, 2, 3, 4]:
            report.errors.append("development Dynamic Programming awaiting-review requires all four batches")
        for batch in completed[:4]:
            for algorithm_id in DYNAMIC_PROGRAMMING_BATCHES[batch - 1]:
                record = algorithms.get(algorithm_id, {})
                if not all(record.get(field) in ARTIFACT_STATUSES for field in STATUS_FIELDS[:3]) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(f"development Dynamic Programming requires completed/tested {algorithm_id}")
        return
    if state.get("scope") == "Divide & Conquer category only" and valid_completed:
        batches = (("maximum-subarray-divide-and-conquer", "karatsuba-multiplication"),
                   ("closest-pair-of-points", "strassen-matrix-multiplication"))
        if len(completed) > 2:
            report.errors.append("development Divide & Conquer has only two batches")
        if status == "in-progress" and (type(active) is not int or active not in (1, 2)):
            report.errors.append("development Divide & Conquer active_batch must be 1 or 2")
        if status == "awaiting-review" and completed != [1, 2]:
            report.errors.append("development Divide & Conquer awaiting-review requires both batches")
        ready_ids = [name for batch in completed[:2] for name in batches[batch-1]]
        ready_ids += ["merge-sort", "quick-sort", "binary-search"]
        for algorithm_id in ready_ids:
            record = algorithms.get(algorithm_id, {})
            if not all(isinstance(record.get(field), str) and record[field] in ARTIFACT_STATUSES
                       for field in STATUS_FIELDS[:3]) or record.get("test_status") not in ("tested", "reviewed"):
                report.errors.append(f"development Divide & Conquer requires completed/tested {algorithm_id}")
        return
    if state.get("scope") == "Recursion & Backtracking category only" and valid_completed:
        if len(completed) > 3:
            report.errors.append("development Recursion & Backtracking has only three batches")
        if status == "in-progress" and (
            type(active) is not int or active not in (1, 2, 3)
        ):
            report.errors.append("development Recursion & Backtracking active_batch must be 1, 2, or 3")
        if status == "awaiting-review" and completed != [1, 2, 3]:
            report.errors.append("development Recursion & Backtracking awaiting-review requires all three batches")
        for batch in completed[:3]:
            for algorithm_id in RECURSION_BACKTRACKING_BATCHES[batch - 1]:
                record = algorithms.get(algorithm_id, {})
                if not all(
                    isinstance(record.get(field), str)
                    and record[field] in ARTIFACT_STATUSES for field in STATUS_FIELDS[:3]
                ) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(
                        f"development: completed recursion/backtracking batch {batch} requires {algorithm_id} "
                        "with completed documentation, both implementations, and tested/reviewed tests"
                    )
        return
    if state.get("scope") == "Searching category only" and valid_completed:
        if len(completed) > 2:
            report.errors.append("development Searching scope has only two batches")
        if status == "in-progress" and (
            type(active) is not int or active not in (1, 2)
        ):
            report.errors.append("development Searching active_batch must be 1 or 2")
        if status == "awaiting-review" and completed != [1, 2]:
            report.errors.append("development Searching awaiting-review requires both completed batches")
        for batch in completed[:2]:
            for algorithm_id in SEARCHING_BATCHES[batch - 1]:
                record = algorithms.get(algorithm_id, {})
                if not all(
                    isinstance(record.get(field), str)
                    and record[field] in ARTIFACT_STATUSES
                    for field in STATUS_FIELDS[:3]
                ) or record.get("test_status") not in ("tested", "reviewed"):
                    report.errors.append(
                        f"development: completed searching batch {batch} requires {algorithm_id} "
                        "with completed documentation, both implementations, and tested/reviewed tests"
                    )
        return
    if state.get("scope") != "Sorting category only" or not valid_completed:
        return
    if len(completed) > len(SORTING_BATCHES):
        report.errors.append("development Sorting scope has only three batches")
    if status == "in-progress" and (
        type(active) is not int or active not in (1, 2, 3)
    ):
        report.errors.append("development Sorting active_batch must be 1, 2, or 3")
    if status == "awaiting-review" and completed != [1, 2, 3]:
        report.errors.append("development Sorting awaiting-review requires all three completed batches")
    for batch in completed[:len(SORTING_BATCHES)]:
        for algorithm_id in SORTING_BATCHES[batch - 1]:
            record = algorithms.get(algorithm_id, {})
            artifacts_ready = all(
                isinstance(record.get(field_name), str)
                and record[field_name] in ARTIFACT_STATUSES
                for field_name in ("documentation_status", "python_status", "cpp_status")
            )
            tests_ready = (
                isinstance(record.get("test_status"), str)
                and record["test_status"] in ("tested", "reviewed")
            )
            if not artifacts_ready or not tests_ready:
                report.errors.append(
                    f"development: completed sorting batch {batch} requires {algorithm_id} "
                    "with completed documentation, both implementations, and tested/reviewed tests"
                )


def _strip_code(text: str) -> str:
    """Remove fenced code and inline code so example links are not interpreted."""
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            value = marker.group(1)
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence):
                fence = None
            continue
        if fence is None and not line.startswith("    "):
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def _anchors(text: str) -> set[str]:
    # Keep inline code contents, which GitHub includes in heading anchors.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    headings = []
    fence = False
    for line in text.splitlines():
        if re.match(r"^\s{0,3}(?:`{3,}|~{3,})", line):
            fence = not fence
        if not fence:
            match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
            if match:
                headings.append(match.group(1))
    anchors = set(re.findall(r"<(?:[^>]+\s)?(?:id|name)=[\"']([^\"']+)[\"']", text))
    counts: Counter[str] = Counter()
    for heading in headings:
        heading = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading)
        heading = html.unescape(re.sub(r"<[^>]+>", "", heading)).lower()
        slug = re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")
        count = counts[slug]
        counts[slug] += 1
        anchors.add(f"{slug}-{count}" if count else slug)
    return anchors


def _link_destinations(text: str) -> tuple[list[str], list[str]]:
    """Read ordinary inline/image/HTML and full/collapsed/shortcut reference links."""
    text = _strip_code(text)
    references: dict[str, str] = {}
    definition = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+).*$", re.MULTILINE)
    def normalize(label: str) -> str:
        return " ".join(label.split()).casefold()

    for match in definition.finditer(text):
        references[normalize(match.group(1))] = match.group(2).strip("<>")
    text = definition.sub("", text)
    links = list(references.values())
    missing = []
    inline = re.compile(
        r"!?\[[^\]\n]*\]\(\s*(<[^>]*>|(?:[^\s()]|\([^()]*\))*)"
        r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
    )
    for match in inline.finditer(text):
        links.append(match.group(1).strip("<>"))
    text = inline.sub("", text)
    reference = re.compile(r"!?\[([^\]\n]+)\]\[([^\]\n]*)\]")
    for match in reference.finditer(text):
        label = normalize(match.group(2) or match.group(1))
        if label not in references:
            missing.append(label)
    text = reference.sub("", text)
    # Shortcut references are links only when a matching definition exists.
    for match in re.finditer(r"!?\[([^\]\n]+)\]", text):
        label = normalize(match.group(1))
        if label in references:
            links.append(references[label])
    links.extend(re.findall(r"\b(?:href|src)=[\"']([^\"']+)[\"']", text))
    return links, missing


def validate_markdown(root: Path, report: ValidationReport) -> None:
    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in (".md", ".markdown")
        and not set(path.relative_to(root).parts) & IGNORED_DIRS
    )
    anchor_cache: dict[Path, set[str]] = {}
    for source in files:
        report.markdown_files += 1
        label = source.relative_to(root).as_posix()
        links, missing = _link_destinations(source.read_text(encoding="utf-8"))
        report.errors.extend(f"{label}: undefined reference link [{ref}]" for ref in missing)
        for destination in links:
            try:
                url = urlsplit(html.unescape(destination))
            except ValueError:
                report.errors.append(f"{label}: malformed link {destination!r}")
                continue
            if url.scheme or url.netloc:
                continue
            report.local_links += 1
            link_path = unquote(url.path)
            target = (
                (root / link_path.lstrip("/")) if link_path.startswith("/")
                else (source.parent / link_path if link_path else source)
            ).resolve()
            if not target.is_relative_to(root):
                report.errors.append(f"{label}: link leaves repository: {destination}")
                continue
            if not target.exists():
                report.errors.append(f"{label}: broken relative link: {destination}")
                continue
            if url.fragment:
                if target.is_dir():
                    target = target / "README.md"
                if not target.is_file() or target.suffix.lower() not in (".md", ".markdown"):
                    report.errors.append(f"{label}: anchor target is not Markdown: {destination}")
                    continue
                if target not in anchor_cache:
                    anchor_cache[target] = _anchors(target.read_text(encoding="utf-8"))
                if unquote(url.fragment) not in anchor_cache[target]:
                    report.errors.append(f"{label}: broken heading anchor: {destination}")


def validate_repository(root: Path) -> ValidationReport:
    root = root.resolve()
    report = ValidationReport()
    try:
        catalog = yaml.load(
            (root / "catalog.yaml").read_text(encoding="utf-8"), Loader=UniqueKeyLoader
        )
        syllabus = json.loads(
            (root / "tests/fixtures/required_syllabus.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        report.errors.append(f"Cannot load catalog or required syllabus: {exc}")
        return report
    if not isinstance(catalog, dict):
        report.errors.append("catalog.yaml must contain a mapping")
        return report
    if type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1:
        report.errors.append("schema_version must be integer 1")
    if catalog.get("project") != "Algorithm Atlas":
        report.errors.append("project must be Algorithm Atlas")
    if not isinstance(syllabus, dict) or not isinstance(syllabus.get("categories"), list):
        report.errors.append("Required syllabus fixture must contain a categories list")
        return report
    categories = catalog.get("categories")
    algorithms = catalog.get("algorithms")
    if not isinstance(categories, list) or not isinstance(algorithms, list):
        report.errors.append("categories and algorithms must be lists")
        return report
    report.categories = len(categories)
    report.canonical_algorithms = len(algorithms)
    expected = {category["id"]: category for category in syllabus["categories"]}
    category_map: dict[str, dict] = {}
    category_paths: set[str] = set()
    references: list[tuple[str, str, str]] = []
    for category in categories:
        if not isinstance(category, dict) or not {
            "id", "name", "path", "items"
        } <= category.keys():
            report.errors.append("Every category needs id, name, path, and items")
            continue
        cid = category["id"]
        if not isinstance(cid, str):
            report.errors.append("Category IDs must be strings")
            continue
        if cid in category_map:
            report.errors.append(f"Duplicate category ID: {cid}")
        category_map[cid] = category
        baseline = expected.get(cid)
        if baseline is None:
            report.errors.append(f"Unknown syllabus category: {cid}")
        elif any(category[key] != baseline[key] for key in ("name", "path")):
            report.errors.append(f"{cid}: category name/path differs from required syllabus")
        path = _relative_path(root, category["path"])
        if path is None:
            report.errors.append(f"{cid}: category path must use safe lowercase kebab-case")
        else:
            if category["path"] in category_paths:
                report.errors.append(f"Duplicate category path: {category['path']}")
            category_paths.add(category["path"])
            if not (path / "README.md").is_file():
                report.errors.append(f"{cid}: missing category README.md")
        items = category["items"]
        if not isinstance(items, list):
            report.errors.append(f"{cid}: items must be a list")
            continue
        labels = []
        report.syllabus_entries += len(items)
        for item in items:
            if (
                not isinstance(item, dict)
                or not _nonempty(item.get("name"))
                or not _nonempty(item.get("algorithm"))
            ):
                report.errors.append(f"{cid}: each syllabus item needs name and algorithm strings")
                continue
            labels.append(item["name"])
            references.append((cid, item["name"], item["algorithm"]))
        if baseline is not None and labels != baseline["items"]:
            missing = list((Counter(baseline["items"]) - Counter(labels)).elements())
            extra = list((Counter(labels) - Counter(baseline["items"])).elements())
            report.errors.append(
                f"{cid}: syllabus mismatch "
                f"(missing={missing}, extra={extra}; order must match)"
            )
    for cid in sorted(expected.keys() - category_map.keys()):
        report.errors.append(f"Missing syllabus category: {cid}")
    algorithm_map: dict[str, dict] = {}
    canonical_names: set[str] = set()
    locations: set[str] = set()
    for algorithm in algorithms:
        if not isinstance(algorithm, dict) or not ALGORITHM_FIELDS <= algorithm.keys():
            report.errors.append("Every algorithm must provide all required catalog fields")
            continue
        aid = algorithm["id"]
        if not isinstance(aid, str) or not KEBAB.fullmatch(aid):
            report.errors.append(f"Invalid canonical algorithm ID: {aid!r}")
            continue
        if aid in algorithm_map:
            report.errors.append(f"Duplicate canonical algorithm ID: {aid}")
        algorithm_map[aid] = algorithm
        for key in ("name", "notes"):
            if not _nonempty(algorithm[key]):
                report.errors.append(f"{aid}: {key} must be a nonempty string")
        if _nonempty(algorithm["name"]):
            normalized_name = " ".join(algorithm["name"].split()).casefold()
            if normalized_name in canonical_names:
                report.errors.append(f"Duplicate canonical algorithm name: {algorithm['name']}")
            canonical_names.add(normalized_name)
        if algorithm["difficulty"] not in ("beginner", "intermediate", "advanced"):
            report.errors.append(f"{aid}: invalid difficulty")
        for key in STATUS_FIELDS:
            if not isinstance(algorithm[key], str) or algorithm[key] not in STATUSES:
                report.errors.append(f"{aid}: invalid {key}: {algorithm[key]!r}")
        category_id = algorithm["category"]
        category = category_map.get(category_id) if isinstance(category_id, str) else None
        if category is None:
            report.errors.append(f"{aid}: unknown canonical category: {category_id!r}")
        elif algorithm["canonical_location"] != f"{category['path']}/{aid}":
            report.errors.append(f"{aid}: canonical_location must equal its category path plus ID")
        path = _relative_path(root, algorithm["canonical_location"])
        if path is None:
            report.errors.append(f"{aid}: canonical location must use safe lowercase kebab-case")
            continue
        if algorithm["canonical_location"] in locations:
            report.errors.append(
                f"Duplicate canonical location: {algorithm['canonical_location']}"
            )
        locations.add(algorithm["canonical_location"])
        readme = path / "README.md"
        if not readme.is_file() or not readme.read_text(encoding="utf-8").strip():
            report.errors.append(f"{aid}: missing or empty canonical README.md")
        elif (
            isinstance(algorithm["documentation_status"], str)
            and algorithm["documentation_status"] in ARTIFACT_STATUSES
        ):
            text = readme.read_text(encoding="utf-8")
            for number, title in enumerate(SECTIONS, 1):
                pattern = rf"^##\s+{number}\.\s+{re.escape(title)}\s*$"
                if not re.search(pattern, text, re.MULTILINE):
                    report.errors.append(
                        f"{aid}: completed documentation missing section {number}. {title}"
                    )
        artifacts = {
            "python_status": (path / "python/solution.py",),
            "cpp_status": (path / "cpp/solution.cpp",),
            "test_status": (path / "tests/test_python.py", path / "tests/test_cpp.py"),
        }
        for status_field, required in artifacts.items():
            status = algorithm[status_field]
            if not isinstance(status, str):
                continue
            for artifact in required:
                exists = artifact.is_file() and bool(artifact.read_text(encoding="utf-8").strip())
                if status in ARTIFACT_STATUSES and not exists:
                    report.errors.append(
                        f"{aid}: {status_field}={status} requires {artifact.relative_to(root)}"
                    )
                if status in ("planned", "blocked") and artifact.exists():
                    report.errors.append(
                        f"{aid}: artifact exists while {status_field} is {status}"
                    )
        if algorithm["test_status"] in ("tested", "reviewed"):
            if any(
                not isinstance(algorithm[key], str)
                or algorithm[key] not in ARTIFACT_STATUSES
                for key in ("documentation_status", "python_status", "cpp_status")
            ):
                report.errors.append(
                    f"{aid}: tested/reviewed tests require completed documentation "
                    "and both implementations"
                )
        if any(
            algorithm[key] in ("tested", "reviewed")
            for key in ("python_status", "cpp_status")
        ):
            if algorithm["test_status"] not in ("tested", "reviewed"):
                report.errors.append(
                    f"{aid}: tested/reviewed implementation requires tested/reviewed tests"
                )
    referenced = set()
    for cid, name, aid in references:
        referenced.add(aid)
        if aid not in algorithm_map:
            report.errors.append(f"{cid}/{name}: unknown canonical algorithm: {aid}")
    for aid, algorithm in algorithm_map.items():
        if aid not in referenced:
            report.errors.append(f"{aid}: canonical record has no syllabus reference")
        if not any(cid == algorithm["category"] and ref == aid for cid, _, ref in references):
            report.errors.append(
                f"{aid}: canonical category must contain a syllabus reference to it"
            )
        related = algorithm["related_algorithms"]
        if not isinstance(related, list) or not all(isinstance(ref, str) for ref in related):
            report.errors.append(f"{aid}: related_algorithms must be a list of IDs")
        else:
            if len(set(related)) != len(related):
                report.errors.append(f"{aid}: duplicate related algorithm references")
            for ref in related:
                if ref not in algorithm_map or ref == aid:
                    report.errors.append(f"{aid}: invalid related algorithm reference: {ref}")
    if "development" in catalog:
        _validate_development(root, catalog["development"], algorithm_map, report)
    validate_markdown(root, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    report = validate_repository(args.root)
    print(
        f"Checked {report.categories} categories, {report.syllabus_entries} syllabus entries, "
        f"{report.canonical_algorithms} canonical algorithms, "
        f"{report.markdown_files} Markdown files, "
        f"and {report.local_links} local links."
    )
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(report.errors)} error(s).", file=sys.stderr)
        return 1
    print("Validation passed. Test execution and external URLs are checked separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
