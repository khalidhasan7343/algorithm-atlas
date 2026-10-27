"""Track-aware structural checks must relax ML only, never DSA guarantees."""
import json
from pathlib import Path

import pytest
import yaml

from scripts.track_policy import is_complete
from scripts.validate_catalog import SECTIONS, validate_repository


@pytest.fixture
def ready_repo(tmp_path):
    def build(ml=True, cpp=False):
        category = dict(id="B1" if ml else "A1", name="Regression" if ml else "Sorting",
                        path="machine-learning/supervised-learning/regression" if ml else "dsa/sorting")
        record = dict(id="sample-topic", name="Sample Topic", category=category["id"],
                      canonical_location=category["path"] + "/sample-topic", difficulty="beginner",
                      documentation_status="implemented", python_status="tested",
                      cpp_status="tested" if cpp else "planned", test_status="tested",
                      related_algorithms=[], notes="Synthetic structural fixture, not a real algorithm.")
        data = dict(schema_version=1, project="Algorithm Atlas",
                    categories=[dict(category, items=[dict(name="Sample Topic", algorithm="sample-topic")])],
                    algorithms=[record])
        (tmp_path / "catalog.yaml").write_text(yaml.safe_dump(data))
        baseline = tmp_path / "tests/fixtures/required_syllabus.json"
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_text(json.dumps(dict(categories=[dict(category, items=["Sample Topic"])])))
        folder = tmp_path / record["canonical_location"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder.parent / "README.md").write_text("# Category\n")
        (folder / "README.md").write_text("\n\n".join(f"## {i}. {title}\n\nFixture content." for i, title in enumerate(SECTIONS, 1)))
        for name in ("python/solution.py", "tests/test_python.py") + (("cpp/solution.cpp", "tests/test_cpp.py") if cpp else ()):
            p = folder / name
            p.parent.mkdir(exist_ok=True)
            p.write_text("# Structural test fixture only\n")
        return tmp_path, data, folder
    return build


@pytest.mark.parametrize("ml,cpp,valid", [(True, False, True), (True, True, True), (False, True, True), (False, False, False)])
def test_required_languages_follow_track(ready_repo, ml, cpp, valid):
    root, data, _ = ready_repo(ml, cpp)
    result = validate_repository(root)
    assert result.ok is valid, result.errors
    assert is_complete(data["algorithms"][0]) is valid


@pytest.mark.parametrize("ml", [False, True])
@pytest.mark.parametrize("missing", ["python/solution.py", "tests/test_python.py"])
def test_python_source_and_tests_are_required_for_both(ready_repo, ml, missing):
    root, _, folder = ready_repo(ml, not ml)
    (folder / missing).unlink()
    assert any(missing in error for error in validate_repository(root).errors)


@pytest.mark.parametrize("missing", ["cpp/solution.cpp", "tests/test_cpp.py"])
def test_partial_optional_cpp_is_rejected(ready_repo, missing):
    root, _, folder = ready_repo(True, True)
    (folder / missing).unlink()
    assert any("optional C++ requires" in e for e in validate_repository(root).errors)


def test_cpp_test_without_source_is_not_silently_ignored(ready_repo):
    root, _, folder = ready_repo(True, False)
    (folder / "tests/test_cpp.py").write_text("# incomplete optional pair\n")
    assert any("optional C++ requires" in e for e in validate_repository(root).errors)


@pytest.mark.parametrize("defect", ["duplicate", "path"])
def test_ml_policy_cannot_bypass_catalog_identity(ready_repo, defect):
    root, data, _ = ready_repo(True, False)
    if defect == "duplicate":
        data["algorithms"].append(data["algorithms"][0].copy())
    else:
        data["algorithms"][0]["canonical_location"] = "../outside"
    (root / "catalog.yaml").write_text(yaml.safe_dump(data))
    assert not validate_repository(root).ok


def test_python_only_ml_is_complete_in_generated_status(ready_repo):
    from scripts.generate_catalog_docs import overall_status
    _, data, _ = ready_repo(True, False)
    assert overall_status(data["algorithms"][0]) == "complete"
    data["algorithms"][0]["cpp_status"] = "in-progress"
    assert overall_status(data["algorithms"][0]) == "in-progress"
