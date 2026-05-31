import unittest
import json
from pathlib import Path

from witness_table.geometry import check_witness
from witness_table.io import load_witness, points_sha256


ROOT = Path(__file__).resolve().parents[1]


class PublicWitnessTest(unittest.TestCase):
    def test_public_witnesses_verify(self) -> None:
        paths = sorted((ROOT / "data" / "witnesses").glob("n*_*.json"))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path.name):
                n, points, data = load_witness(path)
                stats = check_witness(n, points)
                self.assertTrue(stats.ok, path)
                self.assertEqual(len(points), data["size"])
                self.assertEqual(points_sha256(points), data["points_sha256"])

    def test_pages_data_matches_public_witnesses(self) -> None:
        js_path = ROOT / "docs" / "assets" / "witnesses.js"
        prefix = "window.WITNESS_DATA = "
        text = js_path.read_text(encoding="utf-8").strip()
        self.assertTrue(text.startswith(prefix))
        pages_data = json.loads(text[len(prefix) :].removesuffix(";"))
        self.assertEqual(len(pages_data["rows"]), 40)
        for row in pages_data["rows"]:
            n, points, data = load_witness(ROOT / row["witness_file"])
            self.assertEqual(row["N"], n)
            self.assertEqual(row["points"], [list(p) for p in points])
            self.assertEqual(row["points_sha256"], data["points_sha256"])


if __name__ == "__main__":
    unittest.main()
