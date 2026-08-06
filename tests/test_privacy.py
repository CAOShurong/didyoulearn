import pytest

from didyoulearn.privacy import pseudonymize, public_run


def test_pseudonym_is_stable_within_study_and_changes_with_secret():
    first = pseudonymize("student@example.test", "study-a")
    assert first == pseudonymize("student@example.test", "study-a")
    assert first != pseudonymize("student@example.test", "study-b")
    assert "student" not in first


def test_pseudonym_requires_both_inputs():
    with pytest.raises(ValueError):
        pseudonymize("", "secret")
    with pytest.raises(ValueError):
        pseudonymize("identifier", "")


def test_public_run_removes_default_private_fields():
    released = public_run(
        {
            "run_id": "run-one",
            "transcript": "private",
            "notes": "private",
            "email": "private@example.test",
            "screenshots": ["private.png"],
            "score": 0.8,
        }
    )
    assert released["run_id"] == "run-one"
    assert released["score"] == 0.8
    assert "transcript" not in released
    assert "email" not in released
    assert "release_note" in released
