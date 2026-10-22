# CI missing-report investigation and verified resolution

Prepared 2026-10-22 (Asia/Dhaka). No algorithms, CI workflow, validator rules,
ignore rules, or historical reports were modified by this investigation.

## Finding

A clean Git archive of `8446eab749c22e9c1390331e02206ea862795820`
reproduces **exactly the nine reported validator errors**. Both Sorting reports
were deleted by that commit, and the Searching report had not been committed.
The links and catalog path referenced those absent root files. This is a Git
snapshot/artifact-presence defect, not a Python-version difference.

The correction already exists in commit
`5934255315ecc0e44f054678fcb0f71fc70efd18` (current local `main`): all three
original reports were added there. No further restoration or link rewriting is
needed in that commit. All three working-tree report files exactly match their
committed bytes. `.gitignore` and `git check-ignore --no-index` show no matching
exclusion rule; the historical omission/deletion was not an ignore-rule problem.

## Exact mapping of all nine errors

| # | Validator location | Missing artifact in 8446eab |
| --- | --- | --- |
| 1 | catalog.yaml: development.completion_report | SEARCHING-REVIEW-REPORT.md |
| 2 | README.md | SEARCHING-REVIEW-REPORT.md |
| 3 | README.md | SORTING-FINAL-AUDIT-REPORT.md |
| 4 | docs/audit-evidence/README.md | ../../SORTING-FINAL-AUDIT-REPORT.md |
| 5 | docs/progress.md | ../SEARCHING-REVIEW-REPORT.md |
| 6 | docs/searching-checkpoints.md | ../SEARCHING-REVIEW-REPORT.md |
| 7 | docs/searching-evidence/README.md | ../../SEARCHING-REVIEW-REPORT.md |
| 8 | docs/sorting-checkpoints.md | ../SORTING-REVIEW-REPORT.md |
| 9 | docs/sorting-checkpoints.md | ../SORTING-FINAL-AUDIT-REPORT.md |

The original report filenames/case and relative locations are correct. Reports
were not relocated. No historical link was removed to hide an absent artifact.
The authentic root files are now present in the committed tree, so all nine
errors disappear without changing validator behavior.

Original failure transcript:
[8446eab-catalog.txt](ci-report-evidence/8446eab-catalog.txt).

## Git tracking and branch verification

| Report | Present locally | Tracked and present in HEAD | Matches committed bytes | Bytes |
| --- | --- | --- | --- | ---: |
| SEARCHING-REVIEW-REPORT.md | Yes | Yes | Yes | 19,670 |
| SORTING-REVIEW-REPORT.md | Yes | Yes | Yes | 59,962 |
| SORTING-FINAL-AUDIT-REPORT.md | Yes | Yes | Yes | 22,538 |

The local branch and cached remote refs inspected were:

- `main` and `origin/main`: `5934255315ecc0e44f054678fcb0f71fc70efd18`.
- `origin/copilot/fix-lightweight-checks-job`:
  `c9a8ed51a74080dd38c457aef704ee87775d4f8b`.

Clean archives of **both** tips include all three reports and pass catalog and
generated-document validation. The Copilot branch tip has the same committed
file tree as main. These are locally recorded refs, not a claim that live remote
refs or a particular hosted workflow run were fetched or passed.

The reported hosted run URL/SHA was requested but not supplied. GitHub run pages
and API results were unavailable through the connected browser, and `gh` is not
installed. Therefore the exact hosted failing run cannot be independently
matched to a SHA; its nine errors match the reproduced 8446eab failure exactly.
No hosted workflow was dispatched, rerun, or represented as passing.

## Completion-report safety and pending Phase 4 work

The committed HEAD catalog points to
`RECURSION-BACKTRACKING-REVIEW-REPORT.md`, a safe relative, existing, nonempty,
tracked Markdown file. It passes validation in a clean committed checkout.

The current working-tree catalog points to `DIVIDE-CONQUER-REVIEW-REPORT.md`,
also a safe relative, existing, nonempty Markdown file. It passes the unchanged
validator locally. However, that Phase 4 report and the other Phase 4 additions
are **untracked/uncommitted pending work**. Publishing the Phase 4 catalog/README
without its report, checkpoint, implementations, tests and generated docs would
create a new incomplete checkout. This investigation did not stage, revert,
commit, or publish that existing work, or approve Phase 4 on the owner's behalf.

The three reports involved in the nine errors are already committed; adding
those files again is unnecessary. Pending Phase 4 publication is a separate
review/authorization decision.

## Actual validation and test results

| Snapshot | Catalog/relative links | Generated documentation | Full tests |
| --- | --- | --- | --- |
| Clean Git archive of 8446eab | Failed: exactly 9 missing-report errors | Passed, 260 managed pages | Not rerun; failure reproduction only |
| Clean Git archive of HEAD 5934255 | Passed: 303 Markdown files, 3,776 links | Passed, 251 pages, zero drift | **1,197 passed in 84.30s** |
| Clean Git archive of cached Copilot tip c9a8ed5 | Passed: 303 Markdown files, 3,776 links | Passed, 251 pages, zero drift | Not separately rerun; its tree matches HEAD |
| Current working tree (pending Phase 4 included) | Passed | Passed, 247 pages, zero drift | **1,247 passed in 122.33s** |

Full test commands compiled and executed both C++17 and C++20 via `--require-cpp`.
No failure, skip, error, or timeout occurred in either full test run. The clean
committed archive was produced directly from `git archive`, with no working-tree
or untracked-file overlay, no virtual environment copied into it, and no changes
to the real Git checkout. The existing development interpreter ran its tests.

Only supported Python **3.14.2** is available locally (the three discovered
executable paths all resolve to that version). Python 3.11, 3.12 and 3.13 were not
available and were not claimed as executed. The Ubuntu/GCC hosted matrix was not
run. The observed source-file absence explains the identical validator failures
independently of matrix Python version.

Machine-readable results and original command output are in
[ci-report-evidence](ci-report-evidence/README.md). Git status and full
`git ls-files` output were retained there. Report tracking evidence includes the
SHA-256 and exact byte size of each committed original.

## Reproduce the corrected committed checkout

Run from this repository root with the existing `.venv` and C++ compiler:

```sh
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python -m pytest --require-cpp
git status --short
git ls-files
git ls-tree HEAD -- SEARCHING-REVIEW-REPORT.md SORTING-REVIEW-REPORT.md SORTING-FINAL-AUDIT-REPORT.md
git check-ignore --no-index -v SEARCHING-REVIEW-REPORT.md SORTING-REVIEW-REPORT.md SORTING-FINAL-AUDIT-REPORT.md
```

The final `check-ignore` exits 1 with no output when none of those paths is
ignored; that is the expected result here. To test Git-only content in an isolated
snapshot without the uncommitted Phase 4 overlay:

```sh
ci_snapshot=$(mktemp -d)
git archive HEAD | tar -x -C "$ci_snapshot"
.venv/bin/python "$ci_snapshot/scripts/validate_catalog.py"
.venv/bin/python "$ci_snapshot/scripts/generate_catalog_docs.py" --check
```

The saved clean-checkout full test run used the repository `.venv` interpreter
with the extracted directory as cwd, so pytest discovered only committed files.

## Changes, remaining action, and stop

This task added only this investigation report and its truthful evidence files.
No report contents were fabricated, no genuine audit evidence was replaced,
and no implementation, validator, `.gitignore`, or CI workflow was changed.
Existing uncommitted Phase 4 changes were preserved.

For GitHub Actions, start a **new** workflow run on a branch containing 5934255
or a later complete correction. The current workflow supports workflow_dispatch
(the Actions UI's **Run workflow** on the corrected branch). Simply rerunning an
old failed run keeps its original GITHUB_SHA/GITHUB_REF, so an old 8446eab run
will continue to check out the missing reports. See
[GitHub's rerun semantics](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs).

If the failing hosted run claims to use 5934255 or a later commit, the owner
must provide its run URL/SHA to resolve that discrepancy against the successful
clean snapshot. A fresh hosted matrix result remains unverified.

No commit, push, staging operation, workflow dispatch, publication, algorithm
change, or new-category work was performed. Publishing any new report/evidence
or pending Phase 4 bundle requires the owner's explicit commit/push authorization.
**STOP after this report; no further development is authorized by these checks.**
