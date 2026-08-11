# Changelog

All notable changes to DidYouLearn are documented here.

## [Unreleased]

## [0.1.1] - 2026-08-12

### Added

- Add a tag-gated GitHub Release workflow that tests the source, smoke-tests the
  built wheel, publishes SHA-256 checksums, and attests the wheel and sdist.
- Add CodeQL analysis for Python and browser JavaScript plus Dependabot updates
  for GitHub Actions and Python build tooling.

### Changed

- Pin every third-party GitHub Action to a reviewed commit while retaining the
  readable release tag in comments.
- Make PyPI publishing an explicit dispatch that uploads the exact attested
  GitHub Release files after checksum and provenance verification. This avoids
  presenting a missing account-side Trusted Publisher as a successful automatic
  publication or rebuilding a different source archive.

## [0.1.0] - 2026-08-06

### Added

- Versioned cross-domain learning-task schema.
- Correctness-gated outcome scoring for pretest, post-test, transfer, and retention.
- Deterministic balanced assignment for comparative studies.
- Evidence receipts and privacy-preserving participant pseudonyms.
- Static, local-first study application with import and export.
- Reproducible HTML and JSON reports.
- Demonstration study using explicitly fictional tutor identities and results.
