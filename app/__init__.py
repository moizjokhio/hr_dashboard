"""Compatibility package for running the backend from the workspace root.

This exposes `backend/app` as the top-level `app` package so commands like
`python -m uvicorn app.main:app --reload --port 8001` work from the repository
root as well as from the backend directory.
"""

from __future__ import annotations

from pathlib import Path

_BACKEND_APP_DIR = Path(__file__).resolve().parent.parent / "backend" / "app"

__path__ = [str(_BACKEND_APP_DIR)]
