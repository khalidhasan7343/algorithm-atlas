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
