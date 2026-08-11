"""Validate release identity and write deterministic package checksums."""

from __future__ import annotations

import argparse
import hashlib
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def validate_tag(tag: str) -> str:
    version = package_version()
    expected = f"v{version}"
    if tag != expected:
        raise ValueError(f"release tag {tag!r} does not match package version {expected!r}")

    package_init = (ROOT / "src" / "didyoulearn" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', package_init, re.MULTILINE)
    if not match or match.group(1) != version:
        actual = match.group(1) if match else "missing"
        raise ValueError(f"package __version__ {actual!r} does not match {version!r}")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        raise ValueError(f"CHANGELOG.md has no {version!r} release heading")
    return version


def checksums(distribution_dir: Path) -> list[str]:
    files = sorted(
        path
        for path in distribution_dir.glob("didyoulearn-*")
        if path.suffix == ".whl" or path.name.endswith(".tar.gz")
    )
    if len(files) != 2:
        raise ValueError(f"expected one wheel and one sdist, found {[path.name for path in files]}")
    return [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in files]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--write-checksums", type=Path)
    args = parser.parse_args()

    version = validate_tag(args.tag)
    print(f"release identity verified: didyoulearn {version} ({args.tag})")
    if args.write_checksums:
        lines = checksums(args.write_checksums)
        (args.write_checksums / "SHA256SUMS").write_text(
            "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
        )
        print(f"wrote {args.write_checksums / 'SHA256SUMS'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
