from copy import deepcopy

from didyoulearn.demo import demo_runs, demo_task
from didyoulearn.evidence import canonical_json, make_receipt, sha256_digest, verify_receipt


def test_canonical_hash_ignores_mapping_order():
    left = {"a": 1, "b": 2}
    right = {"b": 2, "a": 1}
    assert canonical_json(left) == canonical_json(right)
    assert sha256_digest(left) == sha256_digest(right)


def test_receipt_verifies_original_material():
    task = demo_task()
    run = demo_runs()[0]
    receipt = make_receipt(
        run=run,
        task=task,
        transcript="fictional transcript",
        created_at="2026-08-06T00:00:00+00:00",
    )
    assert (
        verify_receipt(
            receipt,
            run=run,
            task=task,
            transcript="fictional transcript",
        )
        == []
    )


def test_receipt_detects_tampering():
    task = demo_task()
    run = demo_runs()[0]
    receipt = make_receipt(run=run, task=task, transcript="original")
    changed = deepcopy(run)
    changed["teaching_seconds"] += 1
    failures = verify_receipt(receipt, run=changed, task=task, transcript="edited")
    assert "run hash mismatch" in failures
    assert "transcript hash mismatch" in failures


def test_receipt_does_not_claim_model_identity():
    receipt = make_receipt(run=demo_runs()[0], task=demo_task())
    assert "does not prove commercial model identity" in receipt["claim"]
