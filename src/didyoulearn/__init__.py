"""Outcome-based evaluation for AI tutors."""

from .scoring import score_run, score_study
from .validation import validate_run, validate_task

__all__ = ["score_run", "score_study", "validate_run", "validate_task"]
__version__ = "0.1.1"
