"""
app.py — Backward-compatible entry point.
The main logic has moved to modules/ai_engine.py.
This file re-exports get_senior_guidance for any legacy usage.
"""

from modules.ai_engine import get_task_response


def get_senior_guidance(user_query: str, language: str = "en") -> dict:
    """Legacy wrapper — calls the new ai_engine."""
    return get_task_response(query=user_query, language=language)
