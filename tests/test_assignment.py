import pytest

from didyoulearn.assignment import assign_tutor
from didyoulearn.errors import StudyDesignError


def test_assignment_balances_within_task_and_stratum():
    book = []
    for index in range(12):
        row = assign_tutor(
            participant_id=f"p-{index:03d}",
            task_id="task-one",
            stratum="prior-medium",
            tutors=["atlas", "beacon", "cedar"],
            existing=book,
            salt="fixed-study-salt",
        )
        book.append(row)
    counts = {
        tutor: sum(row["tutor_id"] == tutor for row in book)
        for tutor in ["atlas", "beacon", "cedar"]
    }
    assert counts == {"atlas": 4, "beacon": 4, "cedar": 4}


def test_assignment_is_reproducible_from_same_book():
    kwargs = {
        "participant_id": "p-new",
        "task_id": "task-one",
        "stratum": "default",
        "tutors": ["a", "b"],
        "existing": [],
        "salt": "salt",
    }
    assert assign_tutor(**kwargs) == assign_tutor(**kwargs)


def test_assignment_rejects_same_participant_and_task():
    existing = [
        {
            "participant_id": "p-one",
            "task_id": "task-one",
            "stratum": "default",
            "tutor_id": "a",
        }
    ]
    with pytest.raises(StudyDesignError, match="cannot be assigned"):
        assign_tutor(
            participant_id="p-one",
            task_id="task-one",
            stratum="default",
            tutors=["a", "b"],
            existing=existing,
            salt="salt",
        )


def test_assignment_requires_unique_tutors_and_salt():
    with pytest.raises(StudyDesignError):
        assign_tutor(
            participant_id="p-one",
            task_id="task-one",
            stratum="default",
            tutors=["a", "a"],
            existing=[],
            salt="salt",
        )
    with pytest.raises(StudyDesignError):
        assign_tutor(
            participant_id="p-one",
            task_id="task-one",
            stratum="default",
            tutors=["a", "b"],
            existing=[],
            salt="",
        )
