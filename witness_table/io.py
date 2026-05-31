"""File helpers for public witness-table data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from .geometry import Point, normalize_points

SCHEMA = "koizumi-n-avoiding-witness-v1"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def witness_paths(paths: Iterable[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(path.glob("n*_*.json")))
        else:
            expanded.append(path)
    return sorted(expanded)


def load_witness(path: Path) -> tuple[int, list[Point], dict]:
    data = read_json(path)
    if data.get("schema") != SCHEMA:
        raise ValueError(f"{path}: unsupported schema {data.get('schema')!r}")
    n = data.get("N")
    if not isinstance(n, int):
        raise ValueError(f"{path}: N must be an integer")
    points = normalize_points(data.get("points", []))
    declared_size = data.get("size")
    if declared_size != len(points):
        raise ValueError(f"{path}: declared size {declared_size!r} != point count {len(points)}")
    return n, points, data


def points_sha256(points: Iterable[Point]) -> str:
    payload = json.dumps(list(points), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()

