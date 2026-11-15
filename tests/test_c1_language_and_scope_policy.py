"""Phase27 C1 policy: AI keeps Python+C++, shared A5 memberships are reused, guides survive."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from scripts import generate_catalog_docs as generator
from scripts.track_policy import cpp_required, is_complete, track
from scripts.validate_catalog import SECTIONS, validate_repository

ROOT = Path(__file__).resolve().parents[1]
NEW = ("depth-limited-search", "iterative-deepening-dfs", "uniform-cost-search", "bidirectional-search")


def lesson():
    return "\n\n".join(f"## {i}. {title}\n\nFixture content." for i, title in enumerate(SECTIONS, 1))


@pytest.fixture
def c1_repo(tmp_path):
    """Synthetic repository: one shared A5 topic plus one new C1 topic in a Phase27-like state."""
    a5 = dict(id="A5", name="Graph Algorithms", path="dsa/graph-algorithms")
    c1 = dict(id="C1", name="Uninformed Search", path="artificial-intelligence/uninformed-search")
    records = []
    for topic, category in (("shared-search", a5), ("fixture-search", c1)):
        record = dict(id=topic, name=topic, category=category["id"], canonical_location=f'{category["path"]}/{topic}',
                      difficulty="intermediate", documentation_status="implemented", python_status="tested",
                      cpp_status="tested", test_status="tested", related_algorithms=[], notes="Structural fixture.")
        records.append(record)
        folder = tmp_path / record["canonical_location"]
        folder.mkdir(parents=True)
        (folder / "README.md").write_text(lesson())
        for part in ("python/solution.py", "cpp/solution.cpp", "tests/test_python.py", "tests/test_cpp.py"):
            p = folder / part
            p.parent.mkdir(exist_ok=True)
            p.write_text("# Structural fixture only\n")
        (folder.parent / "README.md").write_text("# Category\n")
    categories = [dict(a5, items=[dict(name="shared-search", algorithm="shared-search")]),
                  dict(c1, items=[dict(name="shared-search", algorithm="shared-search"),
                                  dict(name="fixture-search", algorithm="fixture-search")])]
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/checkpoint.md").write_text("# Fixture checkpoint\n")
    (tmp_path / "docs/report.md").write_text("# Fixture report\n")
    development = dict(
        phase="Phase27", phase_number=27, track="artificial-intelligence", category="C1", scope="C1 only",
        approval="Owner authorized C1.", status="awaiting-review", active_batch=None, completed_batches=[1, 2, 3],
        batch_plan=[["shared-search"], ["fixture-search"], []], category_memberships=["shared-search", "fixture-search"],
        checkpoint="docs/checkpoint.md", completion_report="docs/report.md",
        phase_records={"26": dict(owner_approval="approved", audit_verdict="CONDITIONAL PASS"),
                       "27": dict(owner_approval="pending")},
        current_review=dict(owner_approval="pending"))
    catalog = dict(schema_version=1, project="Algorithm Atlas", development=development,
                   categories=categories, algorithms=records)
    baseline = tmp_path / "tests/fixtures/required_syllabus.json"
    baseline.parent.mkdir(parents=True)
    baseline.write_text(json.dumps(dict(categories=[dict(id=c["id"], name=c["name"], path=c["path"],
                                                         items=[i["name"] for i in c["items"]]) for c in categories])))
    save(tmp_path, catalog)
    return tmp_path, catalog


def save(root, catalog):
    (root / "catalog.yaml").write_text(yaml.safe_dump(catalog))


def test_valid_phase27_state_and_two_language_policy(c1_repo):
    root, catalog = c1_repo
    report = validate_repository(root)
    assert report.ok, report.errors
    record = catalog["algorithms"][1]
    assert track(record) == "artificial-intelligence" and cpp_required(record) and is_complete(record)


@pytest.mark.parametrize("missing", ["cpp/solution.cpp", "tests/test_cpp.py", "python/solution.py", "tests/test_python.py"])
def test_ai_canonicals_require_both_languages(c1_repo, missing):
    root, catalog = c1_repo
    (root / catalog["algorithms"][1]["canonical_location"] / missing).unlink()
    assert not validate_repository(root).ok


@pytest.mark.parametrize("defect", ["python-only", "plan-omits-shared", "plan-duplicates", "shared-moved-to-c1",
                                    "shared-incomplete", "previous-pending", "self-approved", "bad-category",
                                    "early-review", "missing-memberships"])
def test_phase27_development_defects_are_rejected(c1_repo, defect):
    root, catalog = c1_repo
    d, records = catalog["development"], catalog["algorithms"]
    if defect == "python-only":
        records[1]["cpp_status"] = "planned"
        for part in ("cpp/solution.cpp", "tests/test_cpp.py"):
            (root / records[1]["canonical_location"] / part).unlink()
    elif defect == "plan-omits-shared":
        d["batch_plan"] = [[], ["fixture-search"], []]
    elif defect == "plan-duplicates":
        d["batch_plan"] = [["shared-search"], ["fixture-search", "shared-search"], []]
    elif defect == "shared-moved-to-c1":
        records[0]["category"] = "C1"
        records[0]["canonical_location"] = "artificial-intelligence/uninformed-search/shared-search"
    elif defect == "shared-incomplete":
        records[0]["test_status"] = "implemented"
    elif defect == "previous-pending":
        d["phase_records"]["26"]["owner_approval"] = "pending"
    elif defect == "self-approved":
        d["current_review"]["owner_approval"] = "approved"
    elif defect == "bad-category":
        d["category"] = "B4"
    elif defect == "early-review":
        d["completed_batches"] = [1, 2]
    else:
        d.pop("category_memberships")
    save(root, catalog)
    assert not validate_repository(root).ok


def test_ai_phase_preserves_the_exact_dpo_blocker(c1_repo):
    root, catalog = c1_repo
    path = "machine-learning/reinforcement-learning/dynamic-policy-optimization"
    dpo = dict(id="dynamic-policy-optimization", name="DPO", category="B8", canonical_location=path,
               difficulty="advanced", documentation_status="blocked", python_status="blocked", cpp_status="blocked",
               test_status="blocked", related_algorithms=[], notes="Blocked pending clarification.")
    b8 = dict(id="B8", name="Reinforcement Learning", path="machine-learning/reinforcement-learning",
              items=[dict(name="DPO", algorithm=dpo["id"])])
    catalog["algorithms"].append(dpo)
    catalog["categories"].append(b8)
    (root / path).mkdir(parents=True)
    (root / path / "README.md").write_text("# Blocked\n")
    (root / b8["path"] / "README.md").write_text("# Category\n")
    (root / "tests/fixtures/required_syllabus.json").write_text(json.dumps(dict(categories=[
        dict(id=c["id"], name=c["name"], path=c["path"], items=[i["name"] for i in c["items"]]) for c in catalog["categories"]])))
    catalog["development"]["dpo_specification_decision"] = dict(decision="remain-blocked", owner_approval="approved",
                                                                substitution_authorized=False)
    save(root, catalog)
    assert validate_repository(root).ok
    changed = copy.deepcopy(catalog)
    changed["development"]["dpo_specification_decision"]["substitution_authorized"] = True
    save(root, changed)
    assert not validate_repository(root).ok


def test_authored_category_guide_is_preserved_and_drift_detected(c1_repo, monkeypatch):
    root, _ = c1_repo
    monkeypatch.setattr(generator, "ROOT", root)
    monkeypatch.setattr(sys, "argv", ["generator"])
    assert generator.main() == 0
    readme = root / "artificial-intelligence/uninformed-search/README.md"
    guide = "\n" + generator.AUTHORED_MARKER + "\n\n## Hand-written guide\n\nKeep me byte-for-byte.\n"
    readme.write_text(readme.read_text() + guide)
    assert generator.main() == 0 and readme.read_text().endswith(guide)
    monkeypatch.setattr(sys, "argv", ["generator", "--check"])
    assert generator.main() == 0
    head, tail = readme.read_text().split(generator.AUTHORED_MARKER)
    readme.write_text(head.replace("Uninformed Search", "Edited Search", 1) + generator.AUTHORED_MARKER + tail)
    assert generator.main() == 1  # Edits to the generated part are still drift.


def test_real_catalog_c1_inventory_and_shared_ownership():
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text(encoding="utf-8"))
    records = {a["id"]: a for a in catalog["algorithms"]}
    for topic in NEW:
        assert records[topic]["category"] == "C1" and is_complete(records[topic]) and cpp_required(records[topic])
    for shared in ("breadth-first-search", "depth-first-search"):
        assert records[shared]["category"] == "A5" and is_complete(records[shared])
    state = catalog["development"]
    assert state["phase_number"] == 27 and state["category"] == "C1"
    assert state["phase_records"]["26"]["audit_verdict"] == "CONDITIONAL PASS"
    assert state["phase_records"]["27"]["owner_approval"] == state["current_review"]["owner_approval"] == "pending"
    dpo = records["dynamic-policy-optimization"]
    assert all(dpo[k] == "blocked" for k in ("documentation_status", "python_status", "cpp_status", "test_status"))


def test_c1_tests_are_in_ci_discovery():
    result = subprocess.run([sys.executable, "-m", "pytest", "artificial-intelligence/uninformed-search",
                             "--collect-only", "-q"], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0
    for topic in NEW:
        assert f"{topic}/tests/test_python.py" in result.stdout and f"{topic}/tests/test_cpp.py" in result.stdout
    assert "python -m pytest --require-cpp" in (ROOT / ".github/workflows/ci.yml").read_text()
