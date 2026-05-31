#!/usr/bin/env python3
"""Verify public Koizumi N-avoiding witness JSON files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from witness_table.geometry import check_witness
from witness_table.io import load_witness, points_sha256, witness_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[ROOT / "data" / "witnesses"],
        help="witness JSON files or directories (default: data/witnesses)",
    )
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    parser.add_argument("--explain", action="store_true", help="print what the verifier checks")
    return parser.parse_args()


def print_explanation() -> None:
    print(
        """The verifier checks one finite witness at a time.

For a witness S and an integer N, it loops over every triple p,q,r in S,
including repeated triples such as p,p,q.  For each triple it computes:

  A2 = twice the triangle area
  D2 = squared triangle diameter
  gap = (A2 - 2N)^2 - 4D2

The N-avoiding condition |area-N| > diameter is exactly gap > 0.
So a witness is verified when every checked triple has positive gap.
The table column min_gap is the smallest gap found over all triples.
"""
    )


def main() -> int:
    args = parse_args()
    if args.explain:
        print_explanation()

    paths = witness_paths(args.paths)
    if not paths:
        print("no witness files found", file=sys.stderr)
        return 2

    rows = []
    failed = False
    for path in paths:
        n, points, data = load_witness(path)
        stats = check_witness(n, points)
        digest = points_sha256(points)
        expected_digest = data.get("points_sha256")
        digest_ok = expected_digest in (None, digest)
        ok = stats.ok and digest_ok
        failed = failed or not ok
        rows.append((n, len(points), ok, stats, digest, path))

    if not args.quiet:
        print("| N | size | ok | min_gap | triples | sha256 | file |")
        print("|---:|---:|:---:|---:|---:|---|---|")
    for n, size, ok, stats, digest, path in sorted(rows):
        if args.quiet and ok:
            continue
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        status = "yes" if ok else "NO"
        print(
            f"| {n} | {size} | {status} | "
            f"{stats.min_margin_squared_numerator} | "
            f"{stats.triple_count_with_repetition} | "
            f"`{digest[:12]}` | `{rel}` |"
        )
        if stats.violation is not None:
            print(f"  violation: {stats.violation}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
