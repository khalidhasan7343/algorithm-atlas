# Root directory cleanup maintenance report

Owner: **MD.Khalid Hasan**. Repository: [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE). Maintenance only; no algorithm phase is approved by this work. Phase 7 remains awaiting owner review. No algorithm implementation, test, lesson or category file was changed; no commit, push or publication was made.

## Root files and infrastructure preserved

The root retains README.md, LICENSE, AGENTS.md, catalog.yaml, pyproject.toml, conftest.py, requirements-dev.txt, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, .gitignore, .gitattributes and .editorconfig. Established .github/, dsa/, machine-learning/, artificial-intelligence/, docs/, scripts/ and tests/ directories remain. The .git directory, local .venv, ignored caches and .DS_Store were left in place; this task did not delete local environments or operating-system files.

Review reports are indexed under [docs/reviews](../../reviews/README.md); packages are under [artifacts/review-packages](../../../artifacts/review-packages/README.md). This includes the Graph handoff awaiting review, so it does not leave another phase-specific report/package at the root.

## Files moved

All filenames are preserved. Git tracking below describes the pre-cleanup index, which already contained 189 staged Phase 7 changes. That existing work was preserved.

| Original root path | New repository path | Tracking before cleanup |
| --- | --- | --- |
| `DIVIDE-CONQUER-REVIEW-REPORT.md` | `docs/reviews/divide-conquer/DIVIDE-CONQUER-REVIEW-REPORT.md` | tracked |
| `DYNAMIC-PROGRAMMING-REVIEW-REPORT.md` | `docs/reviews/dynamic-programming/DYNAMIC-PROGRAMMING-REVIEW-REPORT.md` | tracked |
| `GRAPH-ALGORITHMS-REVIEW-REPORT.md` | `docs/reviews/graph-algorithms/GRAPH-ALGORITHMS-REVIEW-REPORT.md` | tracked |
| `GREEDY-REVIEW-REPORT.md` | `docs/reviews/greedy/GREEDY-REVIEW-REPORT.md` | tracked |
| `PHASE-0-REPORT.md` | `docs/reviews/phase-0/PHASE-0-REPORT.md` | tracked |
| `RECURSION-BACKTRACKING-REVIEW-REPORT.md` | `docs/reviews/recursion-backtracking/RECURSION-BACKTRACKING-REVIEW-REPORT.md` | tracked |
| `SEARCHING-REVIEW-REPORT.md` | `docs/reviews/searching/SEARCHING-REVIEW-REPORT.md` | tracked |
| `SORTING-FINAL-AUDIT-REPORT.md` | `docs/reviews/sorting/SORTING-FINAL-AUDIT-REPORT.md` | tracked |
| `SORTING-REVIEW-REPORT.md` | `docs/reviews/sorting/SORTING-REVIEW-REPORT.md` | tracked |
| `algorithm-atlas-divide-conquer-review.zip` | `artifacts/review-packages/divide-conquer/algorithm-atlas-divide-conquer-review.zip` | tracked |
| `algorithm-atlas-divide-conquer-review.zip.sha256` | `artifacts/review-packages/divide-conquer/algorithm-atlas-divide-conquer-review.zip.sha256` | tracked |
| `algorithm-atlas-divide-conquer-review.zip.verification.json` | `artifacts/review-packages/divide-conquer/algorithm-atlas-divide-conquer-review.zip.verification.json` | tracked |
| `algorithm-atlas-dynamic-programming-review.zip` | `artifacts/review-packages/dynamic-programming/algorithm-atlas-dynamic-programming-review.zip` | tracked |
| `algorithm-atlas-dynamic-programming-review.zip.sha256` | `artifacts/review-packages/dynamic-programming/algorithm-atlas-dynamic-programming-review.zip.sha256` | tracked |
| `algorithm-atlas-dynamic-programming-review.zip.verification.json` | `artifacts/review-packages/dynamic-programming/algorithm-atlas-dynamic-programming-review.zip.verification.json` | tracked |
| `algorithm-atlas-graph-algorithms-review.zip` | `artifacts/review-packages/graph-algorithms/algorithm-atlas-graph-algorithms-review.zip` | local, untracked |
| `algorithm-atlas-graph-algorithms-review.zip.sha256` | `artifacts/review-packages/graph-algorithms/algorithm-atlas-graph-algorithms-review.zip.sha256` | local, untracked |
| `algorithm-atlas-graph-algorithms-review.zip.verification.json` | `artifacts/review-packages/graph-algorithms/algorithm-atlas-graph-algorithms-review.zip.verification.json` | local, untracked |
| `algorithm-atlas-greedy-review.zip` | `artifacts/review-packages/greedy/algorithm-atlas-greedy-review.zip` | tracked |
| `algorithm-atlas-greedy-review.zip.sha256` | `artifacts/review-packages/greedy/algorithm-atlas-greedy-review.zip.sha256` | tracked |
| `algorithm-atlas-greedy-review.zip.verification.json` | `artifacts/review-packages/greedy/algorithm-atlas-greedy-review.zip.verification.json` | tracked |
| `algorithm-atlas-recursion-backtracking-review.zip` | `artifacts/review-packages/recursion-backtracking/algorithm-atlas-recursion-backtracking-review.zip` | tracked |
| `algorithm-atlas-recursion-backtracking-review.zip.sha256` | `artifacts/review-packages/recursion-backtracking/algorithm-atlas-recursion-backtracking-review.zip.sha256` | tracked |
| `algorithm-atlas-recursion-backtracking-review.zip.verification.json` | `artifacts/review-packages/recursion-backtracking/algorithm-atlas-recursion-backtracking-review.zip.verification.json` | tracked |
| `algorithm-atlas-searching-review.zip` | `artifacts/review-packages/searching/algorithm-atlas-searching-review.zip` | tracked |
| `algorithm-atlas-searching-review.zip.sha256` | `artifacts/review-packages/searching/algorithm-atlas-searching-review.zip.sha256` | tracked |
| `algorithm-atlas-searching-review.zip.verification.json` | `artifacts/review-packages/searching/algorithm-atlas-searching-review.zip.verification.json` | tracked |

Nine reports and eighteen package files moved. Six existing ZIPs total **6,919,849 bytes**; no ZIP was rebuilt, extracted into the source tree or duplicated. All archive/checksum/metadata bytes are unchanged. No Sorting ZIP or associated sidecars existed, so [its package directory](../../../artifacts/review-packages/sorting/README.md) documents the absence; no replacement was fabricated. No Phase 0 package existed. Reports already in docs, including the original foundation handoff, existing checkpoints and CI investigation, stayed in their documentation locations.

## References and tooling

Updated live report/package references in README.md, catalog completion-report metadata, generated progress, active contributor/agent/development guidance, historical checkpoint links, evidence README links, the CI investigation document, and the moved reports themselves. Relative Markdown destinations were rebased from each moved report's new folder. Checksum reproduction commands change into the phase package directory because existing checksum contents use archive basenames.

Five package builders now output under artifacts/review-packages/<phase>/ and create missing output folders. Existing no-overwrite protection, required-report checks and exclusions remain; ZIPs and ZIP sidecars are excluded from future source payloads. Three tracking scripts discover reports recursively under docs/reviews while still requiring all known historical reports. No workflow change was needed: the same catalog/generator/pytest commands apply. The catalog validator and link checks were not weakened.

Historical execution logs, frozen catalogs and hash baselines, changed-file inventories and archive verification JSON retain their original snapshot paths/hashes. These are evidence of prior runs and archived payloads, not live path configuration. The [manifest](manifest.json) maps their old report names to current paths. Every changed report has before/after SHA-256 and reversible text edits. Preservation checks validate the current report hash, undo only those recorded edits and compare the reconstructed bytes with the caller's original historical digest. No exception applies to algorithm files. The Graph scope audit now calls these baseline-byte checks accurately. Its new --check-only mode (also in older scope scripts) avoids overwriting historical evidence during maintenance and package verification.

Future conventions in AGENTS.md, CONTRIBUTING.md and docs/development.md require docs/reviews/<phase-name>/ for reports and artifacts/review-packages/<phase-name>/ for packages. New paths must update metadata, links and tooling; owner-review checkpoints remain mandatory. [Reference inventory before cleanup](reference-inventory-before.json) records the entire non-cache text search.

## Git tracking and ignore findings

Nine reports were tracked in the pre-cleanup index, including the newly staged Graph report. Five archive/checksum/metadata sets were tracked. The three Graph package files were local/untracked and not ignored; they remain available at their new paths without being force-added. All moved required Markdown reports are retained as tracked files and remain unignored. .gitignore is unchanged. The five tracked ZIPs total 5,377,044 bytes, and the Graph ZIP is 1,542,805 bytes; none was silently removed or excluded from existing tracking.

Git compared all nine relocated reports with their pre-cleanup bytes and detected all nine as renames with `--find-renames=20%`. The Sorting report has a large linked inventory whose relative targets change entire long lines; default 50% similarity detects eight of nine, while the Sorting report scores 39%. This is a display/history heuristic, not a relaxed content check: original/current hashes and reversible path edits verify the exact original bytes independently. The staged index confirms **23 committed paths as renames** (eight reports and fifteen package files). The Graph report was already a staged addition before cleanup and remains an addition at its new path; its original-byte comparison independently confirms the move. All nine report paths are tracked/nonempty/unignored. Five tracked package sets retain tracking; the three local Graph package files remain untracked and available. Existing staged algorithm work is preserved. See [Git results](git-results.json) and [nine-report rename comparison](report-rename-detection.json).

## Validation and tests

Working-checkout validation passed:

- Full suite: **1558 passed in 245.87 seconds**, zero failures/skips/timeouts; `--require-cpp` exercised C++17 and C++20.
- Catalog, 35/256/235 inventory and all relative Markdown links passed.
- 217 generated catalog pages: zero drift.
- Graph scope/preservation audit passed with `--check-only`.
- Ten new focused maintenance tests passed (also included in the full suite).
- Six existing ZIP checksums, metadata hashes/sizes and CRC checks passed; eighteen package files retain their original bytes.
- 568 algorithm-tree files, 306 historical evidence files and ten root/CI files are byte-identical.

Actual commands, elapsed times and outputs: [validation execution record](checks-results.json), [full-suite output](full-suite.txt) and [preservation results](preservation-results.json). A clean export of the actual staged Git index passed catalog validation, generated-document checks, tracked-only cleanup preservation/package verification, the Graph scope audit and **254 infrastructure tests in 2.69 seconds**. The full 1558-test suite ran in the working checkout; the clean export ran the infrastructure subset, not a second full algorithm suite. The three untracked Graph package files were explicitly absent in the clean export and accounted for with --tracked-only. See [clean export results](tracked-export-results.json).

The catalog algorithms and category memberships are identical to the pre-cleanup snapshot: **35 categories, 256 syllabus memberships, 235 canonical topics**. Development metadata differs only in completion_report, which resolves to [the existing Graph report](../../reviews/graph-algorithms/GRAPH-ALGORITHMS-REVIEW-REPORT.md). Approval/status and completed-batch values remain unchanged. Hash checks protect **568 files under all three algorithm source trees**, ten unchanged root/CI files and **306 historical non-Markdown evidence files**. Moved report changes are restricted to paths and links; findings, test numbers and historical approval meanings are retained.

The first cleanup validation caught one mis-rebased report self-link and six unrelated lesson self-link normalizations. The report link was corrected and all six lessons restored byte-for-byte before the full test gate. [Initial findings](initial-validation-findings.json) retain that correction. Focused tests verify original-byte reconstruction, tamper rejection, no algorithm hash exceptions, report discovery and five package builders' output/exclusion behavior.

## Risks and limits

Existing ZIPs are immutable historical snapshots and therefore retain their original internal layout and pre-cleanup reports. Their unchanged checksums prove preservation; they do not claim to snapshot this maintenance change. Untracked Graph packages are local and will not appear in a fresh tracked checkout unless the owner later chooses to add them. Package README links point to tracked directory documentation so those local files cannot break hosted Markdown validation. The absent Sorting package cannot be verified. For complete report rename/history display use `git diff --cached --find-renames=20%` or the corresponding `git log --follow --find-renames=20%`; ordinary 50% similarity can display the long Sorting inventory report as a delete/add. Older phase-specific scope audits still enforce their original phase boundaries; later implemented categories are not reclassified as part of this cleanup. Their historical results remain evidence for their respective snapshots.

Hosted GitHub Actions was not triggered or verified. Local validation is separate from hosted CI evidence. No algorithm phase is marked approved, no next category was started, and the Graph implementations are unchanged.

## Reproduction

Run from the repository root:

```sh
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python -m pytest --require-cpp -q
.venv/bin/python scripts/verify_root_cleanup.py
.venv/bin/python scripts/verify_graph_algorithms_scope.py --check-only
```

After the maintenance paths are staged, tracking/ignore verification is:

```sh
.venv/bin/python scripts/verify_root_cleanup.py --git
```

A clean staged-file export can be reproduced without creating a commit (run from the repository root):

```sh
atlas_cleanup_python="$PWD/.venv/bin/python"
atlas_cleanup_snapshot=$(mktemp -d /tmp/atlas-cleanup-check.XXXXXX)
git checkout-index --all --prefix="$atlas_cleanup_snapshot/"
(
  cd "$atlas_cleanup_snapshot"
  "$atlas_cleanup_python" scripts/validate_catalog.py
  "$atlas_cleanup_python" scripts/generate_catalog_docs.py --check
  "$atlas_cleanup_python" scripts/verify_root_cleanup.py --tracked-only
  "$atlas_cleanup_python" scripts/verify_graph_algorithms_scope.py --check-only
  "$atlas_cleanup_python" -m pytest tests --require-cpp -q
)
```

Use `--tracked-only` explicitly, since the three local Graph package files are not tracked. To check a checksum manually, change to its phase folder and run `shasum -a 256 -c <archive>.zip.sha256`; the [package index](../../../artifacts/review-packages/README.md) gives each directory. A temporary packaging smoke test builds outside the repository, validates the extracted current layout, and leaves every historical package unchanged. Observed smoke result: 985 source files, all source bytes matched, CRC passed, no nested archive/ZIP-sidecar payload, and extracted catalog/generator/Graph-scope checks passed. See the [packaging record](package-smoke.json) and [six independent checksum results](checksum-results.json).

**STOP after cleanup and validation. Phase 7 still requires explicit owner approval; no commit or push is authorized.**
