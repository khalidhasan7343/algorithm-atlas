# Missing-report CI evidence

See [the investigation report](../ci-report-fix.md) for the nine-error mapping,
tracked originals, current completion-report distinction, and owner actions.

- `8446eab-catalog.txt`: exact original nine-error reproduction from Git-only content.
- `5934255-catalog.txt`: successful committed-main validation.
- `c9a8ed5-catalog.txt`: successful cached Copilot-tip validation.
- Matching `*-generated-docs.txt` files: actual generated-document checks.
- `checkout-results.json`: revision, extracted snapshot path, report presence and commands.
- `committed-checkout-tests.json` / `.txt`: 1,197 tests passed from the committed tree.
- `working-tree-tests.json` / `.txt`: 1,247 tests passed with pending Phase 4 included.
- `working-tree-validation.json`: local catalog/generated-doc commands.
- `report-tracking.json`: committed report sizes/hashes and completion-report metadata.
- `available-python.json`: supported interpreters discovered; all are Python 3.14.2.
- `git-status.txt` and `git-ls-files.txt`: Git state and tracked inventory.

Historical failure is retained, not mislabeled as passing. No hosted CI pass is
claimed. Relative links, report requirements, CI and tests were not disabled.
