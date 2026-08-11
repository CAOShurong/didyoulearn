import hashlib
from pathlib import Path

import pytest

from scripts.release_gate import checksums, package_version, validate_tag


def test_release_identity_matches_metadata_and_changelog():
    version = package_version()
    assert validate_tag(f"v{version}") == version


def test_release_identity_rejects_wrong_tag():
    with pytest.raises(ValueError, match="does not match package version"):
        validate_tag("v999.0.0")


def test_checksums_cover_exactly_one_wheel_and_sdist(tmp_path: Path):
    wheel = tmp_path / "didyoulearn-1.2.3-py3-none-any.whl"
    sdist = tmp_path / "didyoulearn-1.2.3.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    assert checksums(tmp_path) == [
        f"{hashlib.sha256(wheel.read_bytes()).hexdigest()}  {wheel.name}",
        f"{hashlib.sha256(sdist.read_bytes()).hexdigest()}  {sdist.name}",
    ]


def test_checksums_fail_closed_for_missing_distribution(tmp_path: Path):
    (tmp_path / "didyoulearn-1.2.3-py3-none-any.whl").write_bytes(b"wheel")
    with pytest.raises(ValueError, match="expected one wheel and one sdist"):
        checksums(tmp_path)
