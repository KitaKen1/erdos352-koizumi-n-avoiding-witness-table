"""Exact integer checks for Koizumi N-avoiding lattice witnesses.

The model condition is

    |area(p, q, r) - N| > diam(p, q, r)

for every triple of selected lattice points, with repetitions allowed.  The
verifier avoids floating point arithmetic by using twice-area A2 and squared
diameter D2:

    (A2 - 2N)^2 > 4D2.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import combinations_with_replacement
from math import sqrt
from typing import Iterable, Sequence

Point = tuple[int, int]


@dataclass(frozen=True)
class Violation:
    indices: tuple[int, int, int]
    points: tuple[Point, Point, Point]
    twice_area: int
    diameter_squared: int
    margin_squared_numerator: int


@dataclass(frozen=True)
class WitnessStats:
    ok: bool
    n: int
    size: int
    triple_count_with_repetition: int
    max_diameter_squared: int
    max_twice_area: int
    min_margin_squared_numerator: int | None
    violation: Violation | None = None

    def to_jsonable(self) -> dict:
        data = asdict(self)
        if self.violation is not None:
            data["violation"] = asdict(self.violation)
        return data


def normalize_points(points: Iterable[Sequence[int]]) -> list[Point]:
    """Return points as sorted integer pairs and reject malformed entries."""

    out: list[Point] = []
    for p in points:
        if len(p) != 2:
            raise ValueError(f"point must have two coordinates: {p!r}")
        x, y = p
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError(f"point coordinates must be integers: {p!r}")
        out.append((x, y))
    return sorted(out)


def dist2(p: Point, q: Point) -> int:
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def twice_area(p: Point, q: Point, r: Point) -> int:
    return abs((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]))


def triangle_diameter_squared(p: Point, q: Point, r: Point) -> int:
    return max(dist2(p, q), dist2(p, r), dist2(q, r))


def margin_squared_numerator(n: int, p: Point, q: Point, r: Point) -> int:
    """Return (A2 - 2N)^2 - 4D2 for one triple.

    The triple satisfies the strict N-avoiding condition exactly when this value
    is positive.
    """

    a2 = twice_area(p, q, r)
    d2 = triangle_diameter_squared(p, q, r)
    return (a2 - 2 * n) ** 2 - 4 * d2


def is_allowed_triple(n: int, p: Point, q: Point, r: Point) -> bool:
    return margin_squared_numerator(n, p, q, r) > 0


def check_witness(n: int, points: Iterable[Sequence[int]]) -> WitnessStats:
    pts = normalize_points(points)
    if len(set(pts)) != len(pts):
        seen: set[Point] = set()
        duplicates = [p for p in pts if p in seen or seen.add(p)]
        raise ValueError(f"duplicate points in witness: {duplicates!r}")

    max_d2 = 0
    max_a2 = 0
    min_margin: int | None = None
    triple_count = 0

    for i, j, k in combinations_with_replacement(range(len(pts)), 3):
        p, q, r = pts[i], pts[j], pts[k]
        a2 = twice_area(p, q, r)
        d2 = triangle_diameter_squared(p, q, r)
        margin = (a2 - 2 * n) ** 2 - 4 * d2
        triple_count += 1
        max_d2 = max(max_d2, d2)
        max_a2 = max(max_a2, a2)
        min_margin = margin if min_margin is None else min(min_margin, margin)
        if margin <= 0:
            return WitnessStats(
                ok=False,
                n=n,
                size=len(pts),
                triple_count_with_repetition=triple_count,
                max_diameter_squared=max_d2,
                max_twice_area=max_a2,
                min_margin_squared_numerator=min_margin,
                violation=Violation((i, j, k), (p, q, r), a2, d2, margin),
            )

    return WitnessStats(
        ok=True,
        n=n,
        size=len(pts),
        triple_count_with_repetition=triple_count,
        max_diameter_squared=max_d2,
        max_twice_area=max_a2,
        min_margin_squared_numerator=min_margin,
    )


def approximate_margin(n: int, p: Point, q: Point, r: Point) -> float:
    """Return |area-N|-diameter as a human-readable floating value."""

    return abs(twice_area(p, q, r) / 2 - n) - sqrt(triangle_diameter_squared(p, q, r))

