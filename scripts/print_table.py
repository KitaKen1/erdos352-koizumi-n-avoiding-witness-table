#!/usr/bin/env python3
"""Print a Markdown table from data/witness_table.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data" / "witness_table.json"


def main() -> int:
    data = json.loads(TABLE.read_text(encoding="utf-8"))
    print("| N | verified lower bound | witness |")
    print("|---:|---:|---|")
    for row in data["rows"]:
        print(f"| {row['N']} | {row['lower_bound']} | `{row['witness_file']}` |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

