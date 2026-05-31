#!/usr/bin/env python3
"""Small constructive search for N-avoiding witnesses.

This is a lightweight reproducibility aid, not an optimizer.  It is useful for
finding baseline examples for modest N; the published JSON files remain the
authoritative data for the table.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from witness_table.geometry import Point, check_witness, is_allowed_triple, normalize_points


def candidate_box(n: int) -> list[Point]:
    radius = int(math.ceil(1.15 * math.sqrt(n))) + 4
    return [(x, y) for x in range(-radius, radius + 1) for y in range(-radius, radius + 1)]


def can_add(n: int, current: list[Point], p: Point) -> bool:
    trial = current + [p]
    new = len(trial) - 1
    for i in range(len(trial)):
        for j in range(i, len(trial)):
            if not is_allowed_triple(n, trial[i], trial[j], trial[new]):
                return False
    return True


def translate_to_origin(points: list[Point]) -> list[Point]:
    min_x = min(x for x, _ in points)
    min_y = min(y for _, y in points)
    return normalize_points((x - min_x, y - min_y) for x, y in points)


def radial_prefix_search(n: int, denom: int) -> tuple[list[Point], dict]:
    points = candidate_box(n)
    best: list[Point] = []
    best_meta: dict = {}
    offsets = [(a / denom, b / denom) for a in range(denom) for b in range(denom)]
    for cx, cy in offsets:
        ordered = sorted(points, key=lambda p: ((p[0] - cx) ** 2 + (p[1] - cy) ** 2, p[0], p[1]))
        current: list[Point] = []
        for p in ordered:
            if can_add(n, current, p):
                current.append(p)
            else:
                break
        current = translate_to_origin(current)
        if len(current) > len(best):
            best = current
            best_meta = {"method": "radial_prefix_search", "center_mod_1": [cx, cy], "denom": denom}
    return best, best_meta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("N", type=int)
    parser.add_argument("--denom", type=int, default=4)
    parser.add_argument("--json", action="store_true", help="print the witness JSON payload")
    args = parser.parse_args()

    points, meta = radial_prefix_search(args.N, args.denom)
    stats = check_witness(args.N, points)
    payload = {"N": args.N, "size": len(points), "ok": stats.ok, "meta": meta, "points": points}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"N={args.N} size={len(points)} ok={stats.ok} meta={meta}")
        print(" ".join(f"{x},{y}" for x, y in points))
    return 0 if stats.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

