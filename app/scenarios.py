"""Small, labeled scenarios for the context-selection experiment."""

from __future__ import annotations

import json
from pathlib import Path

SCENARIOS_PATH = Path(__file__).parent / "static" / "scenarios.json"
SCENARIOS = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
