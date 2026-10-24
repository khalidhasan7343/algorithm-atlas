"""Mutation tests show the validator rejects real catalog/documentation errors."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from scripts.validate_catalog import (
    SECTIONS, SORTING_BATCHES, ValidationReport, _validate_development,
    validate_repository,
)


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


def add_development(root: Path, data: dict, *, scope="Future authorized scope") -> dict:
    """Add checkpoint metadata to the existing fake topic fixture."""
    document = root / "docs/checkpoint.md"
    document.parent.mkdir(exist_ok=True)
    document.write_text("# Fixture checkpoint\n\nValidation evidence belongs here.\n")
    state = {
        "phase": "Phase 1", "scope": scope, "approval": "Explicit user approval",
        "status": "in-progress", "active_batch": 1, "completed_batches": [],
        "checkpoint": "docs/checkpoint.md",
    }
    data["development"] = state
    return state


def test_optional_development_preserves_catalogs_without_metadata(sample_repo) -> None:
    root, data = sample_repo
    assert "development" not in data
    assert validate_repository(root).ok


def test_sorting_first_batch_metadata_is_valid_without_claiming_completion(sample_repo) -> None:
    root, data = sample_repo
    add_development(root, data, scope="Sorting category only")
    save(root, data)
    assert validate_repository(root).ok


@pytest.mark.parametrize("state", [None, [], "approved", 1, True])
def test_development_must_be_mapping(sample_repo, state) -> None:
    root, data = sample_repo
    data["development"] = state
    save(root, data)
    assert "development must be a mapping" in errors(root)


@pytest.mark.parametrize("field", ["phase", "scope", "approval"])
@pytest.mark.parametrize("value", [None, "", " \n", [], {}, True])
def test_development_requires_nonempty_strings(sample_repo, field, value) -> None:
    root, data = sample_repo
    add_development(root, data)[field] = value
    save(root, data)
    assert f"development.{field} must be a nonempty string" in errors(root)


@pytest.mark.parametrize("field", [
    "phase", "scope", "approval", "status", "active_batch", "completed_batches", "checkpoint"
])
def test_development_required_fields_cannot_be_omitted(sample_repo, field) -> None:
    root, data = sample_repo
    del add_development(root, data)[field]
    save(root, data)
    assert "development is missing required fields" in errors(root)


@pytest.mark.parametrize("status", ["tested", None, [], {}, True])
def test_development_status_is_restricted(sample_repo, status) -> None:
    root, data = sample_repo
    add_development(root, data)["status"] = status
    save(root, data)
    assert "development.status must be in-progress or awaiting-review" in errors(root)


@pytest.mark.parametrize("completed", [
    None, {}, [1, 3], [2], [1, 1], [True], [1, "2"], [0], [-1]
])
def test_development_completed_batches_require_contiguous_integer_prefix(sample_repo, completed) -> None:
    root, data = sample_repo
    add_development(root, data)["completed_batches"] = completed
    save(root, data)
    assert "development.completed_batches must be a contiguous prefix" in errors(root)


@pytest.mark.parametrize("active", [None, 0, -1, True, "1", [], {}])
def test_development_in_progress_requires_next_integer_batch(sample_repo, active) -> None:
    root, data = sample_repo
    add_development(root, data)["active_batch"] = active
    save(root, data)
    assert "development.active_batch must" in errors(root)


def test_development_cannot_jump_over_uncompleted_batch(sample_repo) -> None:
    root, data = sample_repo
    add_development(root, data).update(completed_batches=[1], active_batch=3)
    save(root, data)
    assert "active_batch must be the next uncompleted batch" in errors(root)


@pytest.mark.parametrize("field", ["checkpoint", "completion_report"])
@pytest.mark.parametrize("path", [
    "/tmp/outside.md", "../outside.md", "docs/../README.md", "docs//checkpoint.md",
    "docs\\checkpoint.md", "C:/outside.md", "docs/missing.md", "docs/checkpoint.txt",
    "docs/empty.md", None, [], True, "docs/null\x00.md",
])
def test_development_document_requires_safe_existing_nonempty_markdown(sample_repo, field, path) -> None:
    root, data = sample_repo
    state = add_development(root, data)
    (root / "docs/empty.md").write_text("  \n")
    (root / "docs/checkpoint.txt").write_text("Not a Markdown filename.\n")
    state[field] = path
    save(root, data)
    assert f"development.{field} must name a safe relative existing nonempty .md file" in errors(root)


@pytest.mark.parametrize("field", ["checkpoint", "completion_report"])
def test_development_documents_reject_symlink_escape(sample_repo, field) -> None:
    root, data = sample_repo
    state = add_development(root, data)
    outside = root.with_name(root.name + "-outside.md")
    outside.write_text("# External fixture\n")
    (root / "docs/external.md").symlink_to(outside)
    state[field] = "docs/external.md"
    save(root, data)
    assert f"development.{field} must name a safe relative" in errors(root)


def test_development_allows_safe_internal_symlink_and_completion_report(sample_repo) -> None:
    root, data = sample_repo
    state = add_development(root, data)
    (root / "docs/internal.md").symlink_to(root / "docs/checkpoint.md")
    state["checkpoint"] = "docs/internal.md"
    state["completion_report"] = "docs/checkpoint.md"
    save(root, data)
    assert validate_repository(root).ok


def test_development_future_scope_has_no_sorting_membership_or_three_batch_limit(sample_repo) -> None:
    root, data = sample_repo
    state = add_development(root, data)
    state.update(completed_batches=[1, 2, 3, 4], active_batch=5)
    save(root, data)
    assert validate_repository(root).ok
    state.update(status="awaiting-review", active_batch=None)
    save(root, data)
    assert validate_repository(root).ok


def test_development_awaiting_review_requires_no_active_batch(sample_repo) -> None:
    root, data = sample_repo
    add_development(root, data).update(status="awaiting-review")
    save(root, data)
    assert "awaiting-review requires active_batch=null" in errors(root)


def test_sorting_checkpoint_cannot_overstate_completed_batch(sample_repo) -> None:
    root, data = sample_repo
    state = add_development(root, data, scope="Sorting category only")
    state.update(completed_batches=[1], active_batch=2)
    save(root, data)
    assert "completed sorting batch 1 requires bubble-sort" in errors(root)


def test_sorting_checkpoint_rejects_fourth_batch(sample_repo) -> None:
    root, data = sample_repo
    state = add_development(root, data, scope="Sorting category only")
    state.update(completed_batches=[1, 2, 3], active_batch=4)
    save(root, data)
    assert "Sorting active_batch must be 1, 2, or 3" in errors(root)
    state.update(completed_batches=[1, 2, 3, 4], active_batch=5)
    save(root, data)
    assert "Sorting scope has only three batches" in errors(root)


def test_sorting_awaiting_review_requires_all_three_batches(sample_repo) -> None:
    root, data = sample_repo
    state = add_development(root, data, scope="Sorting category only")
    state.update(status="awaiting-review", active_batch=None, completed_batches=[1, 2])
    save(root, data)
    assert "Sorting awaiting-review requires all three completed batches" in errors(root)


def completed_sorting_statuses() -> dict:
    """Only fake status dictionaries; historical test execution is not simulated."""
    return {
        algorithm: {
            "documentation_status": "implemented", "python_status": "implemented",
            "cpp_status": "implemented", "test_status": "tested",
        }
        for batch in SORTING_BATCHES for algorithm in batch
    }


def test_sorting_completed_metadata_accepts_all_ready_status_records(sample_repo) -> None:
    root, data = sample_repo
    state = add_development(root, data, scope="Sorting category only")
    state.update(status="awaiting-review", active_batch=None, completed_batches=[1, 2, 3])
    report = ValidationReport()
    _validate_development(root, state, completed_sorting_statuses(), report)
    assert report.ok, report.errors


def searching_statuses():
    """Fixture status records, not assertions of historical execution."""
    return {
        algorithm: {
            "documentation_status": "implemented", "python_status": "implemented",
            "cpp_status": "implemented", "test_status": "tested",
        }
        for algorithm in ("linear-search", "binary-search", "jump-search",
                          "interpolation-search", "exponential-search", "ternary-search")
    }


@pytest.mark.parametrize("completed,active,status", [
    ([], 1, "in-progress"), ([1], 2, "in-progress"),
    ([1, 2], None, "awaiting-review"),
])
def test_searching_checkpoint_accepts_its_two_batch_order(sample_repo, completed, active, status):
    root, data = sample_repo
    state = add_development(root, data, scope="Searching category only")
    state.update(completed_batches=completed, active_batch=active, status=status)
    report = ValidationReport()
    _validate_development(root, state, searching_statuses(), report)
    assert report.ok, report.errors


@pytest.mark.parametrize("completed,active,status,expected", [
    ([1, 2], 3, "in-progress", "Searching active_batch"),
    ([1, 2, 3], 4, "in-progress", "Searching scope has only two batches"),
    ([1], None, "awaiting-review", "Searching awaiting-review"),
])
def test_searching_checkpoint_rejects_invalid_phase_claims(sample_repo, completed, active, status, expected):
    root, data = sample_repo
    state = add_development(root, data, scope="Searching category only")
    state.update(completed_batches=completed, active_batch=active, status=status)
    report = ValidationReport()
    _validate_development(root, state, searching_statuses(), report)
    assert any(expected in error for error in report.errors)


@pytest.mark.parametrize("field,value", [
    ("documentation_status", "planned"), ("python_status", "in-progress"),
    ("cpp_status", None), ("test_status", "implemented"), ("test_status", {}),
])
def test_searching_completed_checkpoint_requires_both_languages_and_tests(sample_repo, field, value):
    root, data = sample_repo
    state = add_development(root, data, scope="Searching category only")
    state.update(completed_batches=[1, 2], active_batch=None, status="awaiting-review")
    algorithms = searching_statuses()
    algorithms["ternary-search"][field] = value
    report = ValidationReport()
    _validate_development(root, state, algorithms, report)
    assert any("completed searching batch 2 requires ternary-search" in error
               for error in report.errors)


@pytest.mark.parametrize("field,value", [
    ("documentation_status", "planned"), ("python_status", "in-progress"),
    ("cpp_status", None), ("test_status", "implemented"), ("test_status", {}),
])
def test_sorting_completed_metadata_requires_ready_artifacts_and_test_evidence_status(sample_repo, field, value) -> None:
    root, data = sample_repo
    state = add_development(root, data, scope="Sorting category only")
    state.update(status="awaiting-review", active_batch=None, completed_batches=[1, 2, 3])
    algorithms = completed_sorting_statuses()
    algorithms["tim-sort"][field] = value
    report = ValidationReport()
    _validate_development(root, state, algorithms, report)
    assert any("completed sorting batch 3 requires tim-sort" in error for error in report.errors)


BACKTRACKING_BATCHES = (
    ("permutations", "combinations", "power-set-generation"),
    ("n-queens", "sudoku-solver", "rat-in-a-maze"),
    ("graph-coloring", "hamiltonian-path", "subset-sum-backtracking"),
)


def backtracking_statuses():
    """Synthetic records test metadata rules, not historical execution."""
    return {name: {"documentation_status": "implemented", "python_status": "implemented",
                   "cpp_status": "implemented", "test_status": "tested"}
            for batch in BACKTRACKING_BATCHES for name in batch}


@pytest.mark.parametrize("completed,active,status", [
    ([], 1, "in-progress"), ([1], 2, "in-progress"),
    ([1, 2], 3, "in-progress"), ([1, 2, 3], None, "awaiting-review"),
])
def test_backtracking_valid_batch_checkpoints(sample_repo, completed, active, status):
    root, data = sample_repo
    state = add_development(root, data, scope="Recursion & Backtracking category only")
    state.update(completed_batches=completed, active_batch=active, status=status)
    report = ValidationReport()
    _validate_development(root, state, backtracking_statuses(), report)
    assert report.ok, report.errors


@pytest.mark.parametrize("completed,active,status,expected", [
    ([1, 2, 3], 4, "in-progress", "active_batch must be 1, 2, or 3"),
    ([1, 2, 3, 4], 5, "in-progress", "has only three batches"),
    ([1, 2], None, "awaiting-review", "awaiting-review requires all three batches"),
])
def test_backtracking_rejects_premature_completion(sample_repo, completed, active, status, expected):
    root, data = sample_repo
    state = add_development(root, data, scope="Recursion & Backtracking category only")
    state.update(completed_batches=completed, active_batch=active, status=status)
    report = ValidationReport()
    _validate_development(root, state, backtracking_statuses(), report)
    assert any(expected in error for error in report.errors)


@pytest.mark.parametrize("field,value", [
    ("documentation_status", "planned"), ("python_status", "in-progress"),
    ("cpp_status", None), ("test_status", "implemented"), ("test_status", {}),
])
def test_backtracking_completed_batch_requires_real_deliverable_statuses(sample_repo, field, value):
    root, data = sample_repo
    state = add_development(root, data, scope="Recursion & Backtracking category only")
    state.update(completed_batches=[1, 2, 3], active_batch=None, status="awaiting-review")
    algorithms = backtracking_statuses()
    algorithms["subset-sum-backtracking"][field] = value
    report = ValidationReport()
    _validate_development(root, state, algorithms, report)
    assert any("batch 3 requires subset-sum-backtracking" in error for error in report.errors)


DIVIDE_IDS = ("maximum-subarray-divide-and-conquer", "karatsuba-multiplication",
              "closest-pair-of-points", "strassen-matrix-multiplication",
              "merge-sort", "quick-sort", "binary-search")


def divide_statuses():
    return {name: {"documentation_status": "implemented", "python_status": "tested",
                   "cpp_status": "tested", "test_status": "tested"} for name in DIVIDE_IDS}


@pytest.mark.parametrize("completed,active,status", [
    ([],1,"in-progress"), ([1],2,"in-progress"), ([1,2],None,"awaiting-review")])
def test_divide_valid_checkpoint(sample_repo,completed,active,status):
    root,data=sample_repo
    state=add_development(root,data,scope="Divide & Conquer category only")
    state.update(completed_batches=completed,active_batch=active,status=status)
    report=ValidationReport()
    _validate_development(root,state,divide_statuses(),report)
    assert report.ok,report.errors


@pytest.mark.parametrize("name",DIVIDE_IDS)
def test_divide_completed_requires_new_and_reused_topics(sample_repo,name):
    root,data=sample_repo
    state=add_development(root,data,scope="Divide & Conquer category only")
    state.update(completed_batches=[1,2],active_batch=None,status="awaiting-review")
    records=divide_statuses();records[name]["test_status"]="planned"
    report=ValidationReport();_validate_development(root,state,records,report)
    assert any(name in e for e in report.errors)


@pytest.mark.parametrize("completed,active,status", [
    ([1],None,"awaiting-review"),([1,2],3,"in-progress"),([1,2,3],4,"in-progress")])
def test_divide_invalid_checkpoint(sample_repo,completed,active,status):
    root,data=sample_repo
    state=add_development(root,data,scope="Divide & Conquer category only")
    state.update(completed_batches=completed,active_batch=active,status=status)
    report=ValidationReport();_validate_development(root,state,divide_statuses(),report)
    assert not report.ok


@pytest.mark.parametrize("completed,active,status", [([],1,"in-progress"),([1],2,"in-progress"),([1,2],3,"in-progress"),([1,2,3],4,"in-progress"),([1,2,3,4],None,"awaiting-review")])
def test_dp_valid_checkpoints(sample_repo,completed,active,status):
    from scripts.validate_catalog import DYNAMIC_PROGRAMMING_SCOPE,DYNAMIC_PROGRAMMING_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=DYNAMIC_PROGRAMMING_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in DYNAMIC_PROGRAMMING_BATCHES for name in batch}
    report=ValidationReport();_validate_development(root,state,records,report)
    assert report.ok,report.errors


@pytest.mark.parametrize("completed,active,status", [([1],None,"awaiting-review"),([1,2,3,4],5,"in-progress"),([1,2,3,4,5],6,"in-progress")])
def test_dp_rejects_premature_review_and_extra_batches(sample_repo,completed,active,status):
    from scripts.validate_catalog import DYNAMIC_PROGRAMMING_SCOPE
    root,data=sample_repo
    state=add_development(root,data,scope=DYNAMIC_PROGRAMMING_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    report=ValidationReport();_validate_development(root,state,{},report)
    assert not report.ok


def test_dp_completed_claim_requires_every_requested_topic(sample_repo):
    from scripts.validate_catalog import DYNAMIC_PROGRAMMING_SCOPE,DYNAMIC_PROGRAMMING_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=DYNAMIC_PROGRAMMING_SCOPE)
    state.update(completed_batches=[1,2,3,4],active_batch=None,status="awaiting-review")
    names=[name for batch in DYNAMIC_PROGRAMMING_BATCHES for name in batch]
    for missing in names:
        records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for name in names if name!=missing}
        report=ValidationReport();_validate_development(root,state,records,report)
        assert any(missing in error for error in report.errors)


@pytest.mark.parametrize("completed,active,status", [([],1,"in-progress"),([1],2,"in-progress"),([1,2],None,"awaiting-review")])
def test_greedy_valid_checkpoint_leaves_graph_planned(sample_repo,completed,active,status):
    from scripts.validate_catalog import GREEDY_SCOPE,GREEDY_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=GREEDY_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in GREEDY_BATCHES for name in batch}
    records.update({name:{"documentation_status":"planned","python_status":"planned","cpp_status":"planned","test_status":"planned"} for name in ("dijkstra","prim","kruskal")})
    report=ValidationReport();_validate_development(root,state,records,report)
    assert report.ok,report.errors


@pytest.mark.parametrize("completed,active,status", [([1],None,"awaiting-review"),([1,2],3,"in-progress"),([1,2,3],4,"in-progress")])
def test_greedy_rejects_premature_review_or_third_batch(sample_repo,completed,active,status):
    from scripts.validate_catalog import GREEDY_SCOPE
    root,data=sample_repo
    state=add_development(root,data,scope=GREEDY_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    report=ValidationReport();_validate_development(root,state,{},report)
    assert not report.ok


@pytest.mark.parametrize("missing",("activity-selection","fractional-knapsack","huffman-coding","job-sequencing-with-deadlines"))
def test_greedy_completed_claim_requires_each_owned_topic(sample_repo,missing):
    from scripts.validate_catalog import GREEDY_SCOPE,GREEDY_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=GREEDY_SCOPE)
    state.update(completed_batches=[1,2],active_batch=None,status="awaiting-review")
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in GREEDY_BATCHES for name in batch if name!=missing}
    report=ValidationReport();_validate_development(root,state,records,report)
    assert any(missing in error for error in report.errors)


@pytest.mark.parametrize("completed,active,status", [([],1,"in-progress"),([1,2,3,4],5,"in-progress"),([1,2,3,4,5],None,"awaiting-review")])
def test_graph_phase_valid_batch_states(sample_repo,completed,active,status):
    from scripts.validate_catalog import GRAPH_SCOPE,GRAPH_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=GRAPH_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in GRAPH_BATCHES for name in batch}
    report=ValidationReport();_validate_development(root,state,records,report)
    assert not report.errors


@pytest.mark.parametrize("completed,active,status", [([1,2,3,4],None,"awaiting-review"),([1,2,3,4,5],6,"in-progress"),([1,2,3,4,5,6],None,"awaiting-review")])
def test_graph_phase_rejects_premature_or_excess_batches(sample_repo,completed,active,status):
    from scripts.validate_catalog import GRAPH_SCOPE
    root,data=sample_repo
    state=add_development(root,data,scope=GRAPH_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    report=ValidationReport();_validate_development(root,state,{},report)
    assert report.errors


def test_graph_phase_requires_every_claimed_algorithm(sample_repo):
    from scripts.validate_catalog import GRAPH_SCOPE,GRAPH_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=GRAPH_SCOPE)
    state.update(completed_batches=[1,2,3,4,5],active_batch=None,status="awaiting-review")
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in GRAPH_BATCHES for name in batch}
    for name in list(records):
        reduced=dict(records);del reduced[name]
        report=ValidationReport();_validate_development(root,state,reduced,report)
        assert any(name in error for error in report.errors)


@pytest.mark.parametrize("completed,active,status", [([],1,"in-progress"),([1,2,3,4],5,"in-progress"),([1,2,3,4,5],None,"awaiting-review")])
def test_tree_phase_valid_states(sample_repo,completed,active,status):
    from scripts.validate_catalog import TREE_SCOPE,TREE_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=TREE_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in TREE_BATCHES for name in batch}
    report=ValidationReport();_validate_development(root,state,records,report)
    assert not report.errors


@pytest.mark.parametrize("completed,active,status", [([1,2,3,4],None,"awaiting-review"),([1,2,3,4,5],6,"in-progress"),([1,2,3,4,5,6],None,"awaiting-review")])
def test_tree_phase_rejects_premature_or_extra_batch(sample_repo,completed,active,status):
    from scripts.validate_catalog import TREE_SCOPE
    root,data=sample_repo
    state=add_development(root,data,scope=TREE_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    report=ValidationReport();_validate_development(root,state,{},report)
    assert report.errors


def test_tree_phase_requires_each_claimed_canonical(sample_repo):
    from scripts.validate_catalog import TREE_SCOPE,TREE_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=TREE_SCOPE)
    state.update(completed_batches=[1,2,3,4,5],active_batch=None,status="awaiting-review")
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in TREE_BATCHES for name in batch}
    for name in list(records):
        reduced=dict(records);del reduced[name]
        report=ValidationReport();_validate_development(root,state,reduced,report)
        assert any(name in error for error in report.errors)


@pytest.mark.parametrize("completed,active,status", [([],1,"in-progress"),([1],2,"in-progress"),([1,2],3,"in-progress"),([1,2,3],None,"awaiting-review")])
def test_string_phase_valid_states(sample_repo,completed,active,status):
    from scripts.validate_catalog import STRING_SCOPE,STRING_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=STRING_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in STRING_BATCHES for name in batch}
    report=ValidationReport();_validate_development(root,state,records,report)
    assert not report.errors


@pytest.mark.parametrize("completed,active,status", [([1,2],None,"awaiting-review"),([1,2,3],4,"in-progress"),([1,2,3,4],None,"awaiting-review")])
def test_string_phase_rejects_premature_or_extra_batch(sample_repo,completed,active,status):
    from scripts.validate_catalog import STRING_SCOPE
    root,data=sample_repo
    state=add_development(root,data,scope=STRING_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    report=ValidationReport();_validate_development(root,state,{},report)
    assert report.errors


def test_string_phase_requires_each_claimed_canonical(sample_repo):
    from scripts.validate_catalog import STRING_SCOPE,STRING_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=STRING_SCOPE)
    state.update(completed_batches=[1,2,3],active_batch=None,status="awaiting-review")
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in STRING_BATCHES for name in batch}
    for name in records:
        reduced=dict(records);del reduced[name]
        report=ValidationReport();_validate_development(root,state,reduced,report)
        assert any(name in error for error in report.errors)


@pytest.mark.parametrize("completed,active,status", [([],1,"in-progress"),([1],2,"in-progress"),([1,2],None,"awaiting-review")])
def test_bit_phase_valid_states(sample_repo,completed,active,status):
    from scripts.validate_catalog import BIT_SCOPE,BIT_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=BIT_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in BIT_BATCHES for name in batch}
    report=ValidationReport();_validate_development(root,state,records,report)
    assert not report.errors


@pytest.mark.parametrize("completed,active,status", [([1],None,"awaiting-review"),([1,2],3,"in-progress"),([1,2,3],None,"awaiting-review")])
def test_bit_phase_rejects_premature_or_extra_batch(sample_repo,completed,active,status):
    from scripts.validate_catalog import BIT_SCOPE
    root,data=sample_repo
    state=add_development(root,data,scope=BIT_SCOPE)
    state.update(completed_batches=completed,active_batch=active,status=status)
    report=ValidationReport();_validate_development(root,state,{},report)
    assert report.errors


def test_bit_phase_requires_each_claimed_canonical(sample_repo):
    from scripts.validate_catalog import BIT_SCOPE,BIT_BATCHES
    root,data=sample_repo
    state=add_development(root,data,scope=BIT_SCOPE)
    state.update(completed_batches=[1,2],active_batch=None,status="awaiting-review")
    records={name:{"documentation_status":"implemented","python_status":"tested","cpp_status":"tested","test_status":"tested"} for batch in BIT_BATCHES for name in batch}
    for name in records:
        reduced=dict(records);del reduced[name]
        report=ValidationReport();_validate_development(root,state,reduced,report)
        assert any(name in error for error in report.errors)


def combined_fixture(root, completed):
    from scripts.validate_catalog import NUMBER_WINDOW_SCOPE,NUMBER_WINDOW_BATCHES
    (root/'docs').mkdir(exist_ok=True)
    for name in ('n11','w12'):
        (root/'docs'/f'{name}.md').write_text('Independent phase record')
    state={'phase':'Phases 11 + 12','scope':NUMBER_WINDOW_SCOPE,'approval':'Explicit owner authorization after Phase 10 approval',
           'status':'awaiting-review' if len(completed)==4 else 'in-progress',
           'active_batch':None if len(completed)==4 else len(completed)+1,'completed_batches':completed,
           'checkpoint':'docs/n11.md','completion_report':'docs/n11.md',
           'completion_reports':{'11':'docs/n11.md','12':'docs/w12.md'},'phase_records':{}}
    for key,cat,offset,doc in [('11','A9',0,'n11'),('12','A10',2,'w12')]:
        count=max(0,min(2,len(completed)-offset))
        status='awaiting-review' if count==2 else 'planned' if key=='12' and len(completed)<2 else 'in-progress'
        state['phase_records'][key]={'phase_number':int(key),'category':cat,'status':status,
            'completed_batches':list(range(1,count+1)),'owner_approval':'pending',
            'checkpoint':f'docs/{doc}.md','completion_report':f'docs/{doc}.md'}
    records={name:{'documentation_status':'implemented','python_status':'tested','cpp_status':'tested','test_status':'tested'} for batch in NUMBER_WINDOW_BATCHES for name in batch}
    return state,records


@pytest.mark.parametrize('completed',[[],[1],[1,2],[1,2,3],[1,2,3,4]])
def test_combined_independent_phase_states(sample_repo,completed):
    root,_=sample_repo
    state,records=combined_fixture(root,completed)
    report=ValidationReport();_validate_development(root,state,records,report)
    assert not report.errors


@pytest.mark.parametrize('tamper',['premature_review','extra_batch','phase11_premature','phase12_premature','approved','same_report','missing_report','wrong_pointer'])
def test_combined_rejects_invalid_progress_or_shared_approval(sample_repo,tamper):
    root,_=sample_repo
    state,records=combined_fixture(root,[1])
    if tamper=='premature_review':state.update(status='awaiting-review',active_batch=None)
    elif tamper=='extra_batch':state.update(completed_batches=[1,2,3,4,5],status='awaiting-review',active_batch=None)
    elif tamper=='phase11_premature':state['phase_records']['11']['status']='awaiting-review'
    elif tamper=='phase12_premature':state['phase_records']['12']['status']='in-progress'
    elif tamper=='approved':state['phase_records']['11']['owner_approval']='approved'
    elif tamper=='same_report':state['completion_reports']['12']='docs/n11.md'
    elif tamper=='missing_report':state['phase_records']['12']['completion_report']='docs/missing.md'
    elif tamper=='wrong_pointer':state['completion_report']='docs/w12.md'
    report=ValidationReport();_validate_development(root,state,records,report)
    assert report.errors


def test_combined_requires_each_completed_algorithm(sample_repo):
    root,_=sample_repo
    state,records=combined_fixture(root,[1,2,3,4])
    for name in records:
        subset=dict(records);del subset[name]
        report=ValidationReport();_validate_development(root,state,subset,report)
        assert any(name in e for e in report.errors)
