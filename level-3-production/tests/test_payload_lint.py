"""Fail if serialized agent JSON is missing required keys."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPACE = ROOT / "src" / "genie" / "apex_l2b.geniespace.json"


def test_space_payload():
    payload = json.loads(SPACE.read_text())
    assert payload.get("version") == 2
    instructions = payload["instructions"]
    assert instructions["text_instructions"]
    assert instructions["example_question_sqls"]
    assert payload["benchmarks"]["questions"]


if __name__ == "__main__":
    test_space_payload()
    print("PASS payload lint")
