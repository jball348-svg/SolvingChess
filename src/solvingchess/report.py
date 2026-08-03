"""Small helpers so every experiment emits results in the same shape.

Each experiment writes a JSON record to ``results/`` and prints a markdown table
to stdout, so a run can be pasted straight into the experiment's ``results.md``
and the raw numbers stay machine-readable for later re-analysis.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


def provenance() -> dict:
    """Enough context to tell whether two runs are comparable."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        commit = "unknown"
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit": commit,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


def save(name: str, payload: dict) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"{name}.json"
    path.write_text(json.dumps({"provenance": provenance(), **payload}, indent=2) + "\n")
    return path


def markdown_table(rows, columns) -> str:
    """``columns`` is a list of ``(header, key, formatter)`` triples."""
    header = "| " + " | ".join(h for h, _, _ in columns) + " |"
    rule = "|" + "|".join("---" for _ in columns) + "|"
    body = []
    for row in rows:
        cells = []
        for _, key, fmt in columns:
            value = row.get(key)
            cells.append("-" if value is None else (fmt(value) if fmt else str(value)))
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, rule] + body)


def integer(value) -> str:
    return f"{value:,}"


def seconds(value) -> str:
    return f"{value:.1f}s"


def percent(value) -> str:
    return f"{value:.2f}%"
