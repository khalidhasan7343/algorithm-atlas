# Repository artifacts

[Review packages](review-packages/README.md) hold immutable phase ZIPs, checksums and verification metadata. Reports live in [docs/reviews](../docs/reviews/README.md). Source, configuration and primary project documentation remain at the root or their established source directories.

Do not rebuild historical ZIPs merely to change their internal layout. Future review ZIPs must snapshot the updated repository, preserve required reports, and exclude environments, caches, secrets, compiled output and nested ZIPs/ZIP sidecars. Keep required Markdown reports tracked; do not force-add ignored archives. No phase approval or publication is implied by artifact organization.
