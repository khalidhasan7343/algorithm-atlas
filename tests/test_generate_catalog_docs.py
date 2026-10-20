"""Protect authored documentation and read-only generated-page checks."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts import generate_catalog_docs as generator


@pytest.fixture
def planning_repo(tmp_path: Path, monkeypatch) -> tuple[Path, dict, Path]:
    """A miniature catalog fixture; no syllabus algorithm is implemented."""
    record = {
        'id': 'sample-topic', 'name': 'Sample Topic', 'category': 'A1',
        'canonical_location': 'dsa/sorting/sample-topic',
        'difficulty': 'beginner', 'documentation_status': 'planned',
        'python_status': 'planned', 'cpp_status': 'planned',
        'test_status': 'planned', 'related_algorithms': [],
        'notes': 'A Unicode planning note: naïve ordering — scope pending.',
    }
    catalog = {
        'schema_version': 1, 'project': 'Algorithm Atlas',
        'categories': [{
            'id': 'A1', 'name': 'Sorting', 'path': 'dsa/sorting',
            'items': [{'name': 'Sample Topic', 'algorithm': 'sample-topic'}],
        }],
        'algorithms': [record],
    }
    save_catalog(tmp_path, catalog)
    monkeypatch.setattr(generator, 'ROOT', tmp_path)
    monkeypatch.setattr('sys.argv', ['generate_catalog_docs.py'])
    readme = tmp_path / record['canonical_location'] / 'README.md'
    return tmp_path, catalog, readme


def save_catalog(root: Path, catalog: dict) -> None:
    (root / 'catalog.yaml').write_text(
        yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False),
        encoding='utf-8',
    )


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob('*') if path.is_file()
    }


def test_unmarked_authored_documentation_is_preserved(planning_repo) -> None:
    _, _, readme = planning_repo
    authored = '# Authored article\n\nA carefully reviewed explanation.\n'
    readme.parent.mkdir(parents=True)
    readme.write_text(authored, encoding='utf-8')

    assert generator.main() == 0

    assert readme.read_text(encoding='utf-8') == authored


@pytest.mark.parametrize('field', generator.STATUS_FIELDS)
@pytest.mark.parametrize('exists', [True, False])
def test_progressed_topic_is_not_replaced_or_fabricated(
    planning_repo, field: str, exists: bool
) -> None:
    root, catalog, readme = planning_repo
    catalog['algorithms'][0][field] = 'in-progress'
    save_catalog(root, catalog)
    authored = generator.PLANNING_MARKER + '\n# Work in progress\n'
    if exists:
        readme.parent.mkdir(parents=True)
        readme.write_text(authored, encoding='utf-8')

    assert generator.main() == 0

    assert readme.exists() is exists
    if exists:
        assert readme.read_text(encoding='utf-8') == authored


def test_pending_managed_page_refreshes_and_preserves_unicode(planning_repo) -> None:
    root, catalog, readme = planning_repo
    assert generator.main() == 0
    assert 'naïve ordering — scope pending.' in readme.read_text(encoding='utf-8')
    catalog['algorithms'][0]['notes'] = 'Revised scope with a different contract.'
    save_catalog(root, catalog)

    assert generator.main() == 0

    content = readme.read_text(encoding='utf-8')
    assert generator.PLANNING_MARKER in content
    assert 'Revised scope with a different contract.' in content
    assert 'naïve ordering — scope pending.' not in content


def test_blocked_topic_gets_honest_planning_page(planning_repo) -> None:
    root, catalog, readme = planning_repo
    for field in generator.STATUS_FIELDS:
        catalog['algorithms'][0][field] = 'blocked'
    save_catalog(root, catalog)

    assert generator.main() == 0

    content = readme.read_text(encoding='utf-8')
    assert '| Full algorithm documentation | blocked |' in content
    assert '| Python implementation | blocked |' in content
    assert 'have not been created' in content


def test_check_reports_drift_without_mutating_files(
    planning_repo, monkeypatch, capsys
) -> None:
    root, _, readme = planning_repo
    readme.parent.mkdir(parents=True)
    readme.write_text(generator.PLANNING_MARKER + '\nStale page.\n', encoding='utf-8')
    before = snapshot(root)
    monkeypatch.setattr('sys.argv', ['generate_catalog_docs.py', '--check'])

    assert generator.main() == 1

    assert snapshot(root) == before
    assert 'Generated documentation needs updating:' in capsys.readouterr().out


def test_generation_is_idempotent_and_check_passes(planning_repo, monkeypatch) -> None:
    root, _, _ = planning_repo
    assert generator.main() == 0
    before = snapshot(root)

    assert generator.main() == 0
    assert snapshot(root) == before
    monkeypatch.setattr('sys.argv', ['generate_catalog_docs.py', '--check'])
    assert generator.main() == 0
    assert snapshot(root) == before
