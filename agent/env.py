"""Load .env once, for every entrypoint.

Without this, a key pasted into .env reaches the wallet module and nothing else,
so the bench aborts saying the variable is missing while it is sitting on disk
two directories up.

Real environment variables always win: `GEMINI_API_KEY=... python -m bench.run`
overrides the file rather than being silently ignored.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_LOADED = False


def load(path: Path | None = None) -> None:
    global _LOADED
    if _LOADED and path is None:
        return
    env = path or (ROOT / ".env")
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    if path is None:
        _LOADED = True
