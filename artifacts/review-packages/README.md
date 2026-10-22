# Phase review packages

Six existing ZIPs and twelve checksum/verification sidecars were relocated without changing their bytes (6,919,849 ZIP bytes total). Five package sets were already tracked. The Graph set was local and untracked; cleanup preserves that status. None was ignored. Availability below describes the working checkout at maintenance time, not a guarantee that local untracked files exist in a fresh clone.

| Phase | Availability at cleanup | ZIP bytes |
| --- | --- | ---: |
| [sorting](sorting/README.md) | no package found | — |
| [searching](searching/README.md) | tracked before cleanup | 810606 |
| [recursion-backtracking](recursion-backtracking/README.md) | tracked before cleanup | 948887 |
| [divide-conquer](divide-conquer/README.md) | tracked before cleanup | 1053768 |
| [dynamic-programming](dynamic-programming/README.md) | tracked before cleanup | 1225605 |
| [greedy](greedy/README.md) | tracked before cleanup | 1338178 |
| [graph-algorithms](graph-algorithms/README.md) | local, untracked before cleanup | 1542805 |

Checksums contain archive basenames, so run shasum from the corresponding phase folder. The verifier also resolves them correctly from the repository root. ZIP metadata describes the unchanged original archived snapshot; historical internal paths should not be rewritten. See [review reports](../../docs/reviews/README.md) and the [maintenance report](../../docs/maintenance/root-cleanup/REPORT.md).

Future ZIPs, SHA-256 sidecars and package JSON belong in artifacts/review-packages/<phase-name>/. Package scripts create their output directory, retain no-overwrite protection, and exclude nested ZIPs and sidecars from source payloads. Markdown reports must remain tracked and unignored. Existing owner-review gates remain mandatory.
