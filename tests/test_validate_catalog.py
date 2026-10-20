"""Mutation tests show the validator rejects real catalog/documentation errors."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from scripts.validate_catalog import SECTIONS, validate_repository


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_repo(tmp_path: Path) -> tuple[Path, dict]:
    """A tiny validation fixture, not an implementation of a syllabus algorithm."""
    category = {"id": "A1", "name": "Sorting", "path": "dsa/sorting"}
    record = {
        "id": "sample-topic", "name": "Sample Topic", "category": "A1",
        "canonical_location": "dsa/sorting/sample-topic", "difficulty": "beginner",
        "documentation_status": "planned", "python_status": "planned",
        "cpp_status": "planned", "test_status": "planned", "related_algorithms": [],
        "notes": "Infrastructure fixture only; implementation awaits a later phase.",
    }
    data = {
        "schema_version": 1, "project": "Algorithm Atlas",
        "categories": [{
            **category, "items": [{"name": "Sample Topic", "algorithm": "sample-topic"}]
        }],
        "algorithms": [record],
    }
    fixture = tmp_path / "tests/fixtures/required_syllabus.json"
    fixture.parent.mkdir(parents=True)
    fixture.write_text(json.dumps({"categories": [{**category, "items": ["Sample Topic"]}]}))
    path = tmp_path / record["canonical_location"]
    path.mkdir(parents=True)
    (path / "README.md").write_text("# Sample Topic\n\nPlanned documentation.\n")
    (path.parent / "README.md").write_text("# Sorting\n")
    save(tmp_path, data)
    return tmp_path, data


def save(root: Path, data: dict) -> None:
    (root / "catalog.yaml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def errors(root: Path) -> str:
    return "\n".join(validate_repository(root).errors)


def test_actual_repository_is_valid() -> None:
    report = validate_repository(REPO_ROOT)
    assert report.ok, "\n".join(report.errors)
    # These totals come from the complete master syllabus, not a generated catalog.
    assert report.categories == 35
    assert report.syllabus_entries == 256


def test_planned_topics_need_no_sources(sample_repo) -> None:
    root, _ = sample_repo
    assert validate_repository(root).ok


def test_cli_succeeds_and_fails_with_useful_exit_codes(sample_repo) -> None:
    root, _ = sample_repo
    command = [sys.executable, str(REPO_ROOT / "scripts/validate_catalog.py"), "--root", str(root)]
    passing = subprocess.run(command, capture_output=True, text=True, timeout=10)
    assert passing.returncode == 0, passing.stderr
    assert "Validation passed" in passing.stdout
    (root / "dsa/sorting/sample-topic/README.md").unlink()
    failing = subprocess.run(command, capture_output=True, text=True, timeout=10)
    assert failing.returncode == 1
    assert "missing or empty canonical README" in failing.stderr


def test_missing_syllabus_item_is_rejected(sample_repo) -> None:
    root, data = sample_repo
    data["categories"][0]["items"] = []
    save(root, data)
    assert "syllabus mismatch" in errors(root)


def test_missing_category_is_rejected(sample_repo) -> None:
    root, data = sample_repo
    data["categories"] = []
    save(root, data)
    assert "Missing syllabus category: A1" in errors(root)


def test_changed_syllabus_wording_is_rejected(sample_repo) -> None:
    root, data = sample_repo
    data["categories"][0]["items"][0]["name"] = "Renamed Topic"
    save(root, data)
    assert "syllabus mismatch" in errors(root)


@pytest.mark.parametrize("target,expected", [
    ("algorithms", "Duplicate canonical algorithm ID"),
    ("categories", "Duplicate category ID"),
])
def test_duplicate_records_are_rejected(sample_repo, target, expected) -> None:
    root, data = sample_repo
    data[target].append(copy.deepcopy(data[target][0]))
    save(root, data)
    assert expected in errors(root)


def test_duplicate_yaml_keys_are_rejected(sample_repo) -> None:
    root, _ = sample_repo
    with (root / "catalog.yaml").open("a") as stream:
        stream.write("schema_version: 1\n")
    assert "Duplicate YAML key" in errors(root)


def test_duplicate_algorithm_name_under_a_new_id_is_rejected(sample_repo) -> None:
    root, data = sample_repo
    duplicate = copy.deepcopy(data["algorithms"][0])
    duplicate.update(
        id="another-topic", name="  SAMPLE TOPIC  ",
        canonical_location="dsa/sorting/another-topic",
    )
    data["algorithms"].append(duplicate)
    save(root, data)
    assert "Duplicate canonical algorithm name" in errors(root)


def test_missing_canonical_readme_is_rejected(sample_repo) -> None:
    root, _ = sample_repo
    (root / "dsa/sorting/sample-topic/README.md").unlink()
    assert "missing or empty canonical README" in errors(root)


def test_missing_category_readme_is_rejected(sample_repo) -> None:
    root, _ = sample_repo
    (root / "dsa/sorting/README.md").unlink()
    assert "missing category README" in errors(root)


@pytest.mark.parametrize("value", [
    "../../outside", "dsa/sorting/Sample", "/tmp/sample", "dsa//sample"
])
def test_unsafe_or_noncanonical_paths_are_rejected(sample_repo, value) -> None:
    root, data = sample_repo
    data["algorithms"][0]["canonical_location"] = value
    save(root, data)
    assert "canonical location must use safe lowercase kebab-case" in errors(root)


def test_dangling_canonical_reference_is_rejected(sample_repo) -> None:
    root, data = sample_repo
    data["categories"][0]["items"][0]["algorithm"] = "unknown"
    save(root, data)
    assert "unknown canonical algorithm: unknown" in errors(root)


@pytest.mark.parametrize("related", [
    ["unknown"], ["sample-topic"], ["unknown", "unknown"], "unknown"
])
def test_invalid_related_references_are_rejected(sample_repo, related) -> None:
    root, data = sample_repo
    data["algorithms"][0]["related_algorithms"] = related
    save(root, data)
    assert "related algorithm" in errors(root) or "related_algorithms" in errors(root)


@pytest.mark.parametrize("field", [
    "documentation_status", "python_status", "cpp_status", "test_status"
])
@pytest.mark.parametrize("status", ["complete", None, [], {}, True])
def test_invalid_status_is_rejected_without_crashing(sample_repo, field, status) -> None:
    root, data = sample_repo
    data["algorithms"][0][field] = status
    save(root, data)
    assert f"invalid {field}" in errors(root)


@pytest.mark.parametrize("field", ["python_status", "cpp_status", "test_status"])
def test_implemented_status_requires_real_artifacts(sample_repo, field) -> None:
    root, data = sample_repo
    data["algorithms"][0][field] = "implemented"
    save(root, data)
    assert f"{field}=implemented requires" in errors(root)


def test_planned_status_cannot_hide_existing_sources(sample_repo) -> None:
    root, _ = sample_repo
    source = root / "dsa/sorting/sample-topic/python/solution.py"
    source.parent.mkdir()
    source.write_text("# Infrastructure fixture: source intentionally omitted.\n")
    assert "artifact exists while python_status is planned" in errors(root)


def test_tested_status_requires_completed_implementation_and_docs(sample_repo) -> None:
    root, data = sample_repo
    data["algorithms"][0]["test_status"] = "tested"
    save(root, data)
    expected = "tested/reviewed tests require completed documentation and both implementations"
    assert expected in errors(root)


def test_tested_implementation_requires_tested_tests(sample_repo) -> None:
    root, data = sample_repo
    data["algorithms"][0]["python_status"] = "tested"
    save(root, data)
    assert "tested/reviewed implementation requires tested/reviewed tests" in errors(root)


def test_completed_documentation_requires_all_25_sections(sample_repo) -> None:
    root, data = sample_repo
    data["algorithms"][0]["documentation_status"] = "implemented"
    save(root, data)
    assert "completed documentation missing section 25. Author Attribution" in errors(root)
    readme = root / "dsa/sorting/sample-topic/README.md"
    readme.write_text("\n\n".join(
        f"## {i}. {title}\n\nFixture content." for i, title in enumerate(SECTIONS, 1)
    ))
    assert validate_repository(root).ok


@pytest.mark.parametrize("link,expected", [
    ("[missing](does-not-exist.md)", "broken relative link"),
    ("[heading](dsa/sorting/README.md#missing)", "broken heading anchor"),
    ("[escape](../outside.md)", "link leaves repository"),
    ("[reference][missing]", "undefined reference link"),
    ("[reference][]", "undefined reference link"),
    ("![image](missing.png)", "broken relative link"),
    ('<a href="missing.md">HTML link</a>', "broken relative link"),
    ("[ref][target]\n\n[target]: missing.md", "broken relative link"),
])
def test_bad_links_are_rejected(sample_repo, link, expected) -> None:
    root, _ = sample_repo
    (root / "README.md").write_text(f"# Fixture\n\n{link}\n")
    assert expected in errors(root)


def test_inline_reference_shortcut_directory_and_anchor_links(sample_repo) -> None:
    root, _ = sample_repo
    (root / "README.md").write_text(
        "# Fixture\n\n## Duplicate\n\n## Duplicate\n\n"
        "[inline](dsa/sorting/README.md#sorting)\n\n"
        "[directory](dsa/sorting/)\n\n[second](#duplicate-1)\n\n"
        "[target][doc]\n\n[doc][]\n\n[doc]\n\n"
        "[doc]: dsa/sorting/README.md \"Reference title\"\n\n"
        "[external](https://example.com/unverified)\n\n"
        "[email](mailto:contact@example.com)\n\n"
        "`[code example](missing.md)`\n\n```markdown\n[example](missing.md)\n```\n"
    )
    assert validate_repository(root).ok


def test_encoded_filename_and_html_anchor(sample_repo) -> None:
    root, _ = sample_repo
    (root / "a file.md").write_text('# Inline `Code`\n\n<a id="explicit"></a>\n')
    (root / "README.md").write_text(
        "[one](a%20file.md#inline-code)\n[two](a%20file.md#explicit)\n"
    )
    assert validate_repository(root).ok


def test_missing_catalog_returns_validation_error(tmp_path) -> None:
    assert "Cannot load catalog" in errors(tmp_path)


@pytest.mark.parametrize("document", [
    "[]", "null", "schema_version: 1\nproject: Algorithm Atlas\ncategories: {}\nalgorithms: []"
])
def test_malformed_catalog_is_rejected(sample_repo, document) -> None:
    root, _ = sample_repo
    (root / "catalog.yaml").write_text(document)
    assert not validate_repository(root).ok
