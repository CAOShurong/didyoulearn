# Publishing DidYouLearn

GitHub Releases are the current authoritative distribution channel. A release
is created only by a version tag that points at the current `main` commit. The
workflow validates the tag against both package version fields and the
changelog, runs the test and lint suite, builds the static site, checks the
wheel and source distribution, installs the wheel into a clean environment,
creates `SHA256SUMS`, and publishes GitHub provenance attestations.

## Release checklist

1. Merge a reviewed version change into `main`.
2. Require the `main` CI, CodeQL, and Pages workflows to succeed.
3. Create an annotated `vX.Y.Z` tag at that exact `main` commit and push it.
4. Wait for the Release workflow to publish the wheel, source distribution,
   checksums, and provenance.
5. Download the public wheel into a clean environment and run `--version`,
   `doctor`, a fictional `demo`, and an expected failure path.

Never move or recreate a published version tag.

## One-time PyPI account setup

The `didyoulearn` project does not yet exist on PyPI. PyPI's documented path is
a [pending Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/),
which creates the project on first successful OIDC upload without a long-lived
API token. The PyPI account owner must add the following exact publisher under
account **Publishing**:

| Field | Value |
|---|---|
| PyPI project name | `didyoulearn` |
| GitHub owner | `CAOShurong` |
| GitHub repository | `didyoulearn` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

The environment value is security-relevant: it must match the workflow's
`pypi` environment exactly. Registering a pending publisher does not reserve
the project name until the first upload.

After the publisher exists and the matching GitHub Release has passed public
verification, dispatch **Publish to PyPI** with its exact tag. The workflow
downloads the exact GitHub Release wheel and source distribution, verifies both
against `SHA256SUMS` and their GitHub provenance, and then uses PyPI's
short-lived OIDC credential. It does not rebuild different archives, contain an
API token, or publish directly from a maintainer laptop.

The previous v0.1.0 attempt failed with `invalid-publisher` because PyPI had no
publisher matching `CAOShurong/didyoulearn`, `publish.yml`, and environment
`pypi`. Rerunning without adding the account-side publisher cannot fix it.
