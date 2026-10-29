import csv
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runner", ROOT / "scripts/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
FREEFEM = os.environ.get("FREEFEM_BIN", "FreeFem++")


@unittest.skipUnless(shutil.which(FREEFEM), "FreeFEM not installed")
class Invariants(unittest.TestCase):
    def test_constant_image_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner.solve(tmp, n=8, steps=3, constant=True, executable=FREEFEM)
            with open(Path(tmp) / "history.csv") as stream: rows = list(csv.DictReader(stream))
            for row in rows:
                self.assertLess(float(row["l2_pm"]), 1e-10)
                self.assertLess(float(row["l2_heat"]), 1e-10)
                self.assertAlmostEqual(float(row["mass_pm"]), .7, places=10)

    def test_no_flux_preserves_mass_and_heat_smooths(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner.solve(tmp, n=24, steps=5, executable=FREEFEM)
            with open(Path(tmp) / "history.csv") as stream: rows = list(csv.DictReader(stream))
            for method in ["pm", "heat"]:
                masses = [float(row[f"mass_{method}"]) for row in rows]
                self.assertLess(max(abs(m - masses[0]) for m in masses), 1e-10)
            energies = [float(row["h1_heat"]) for row in rows]
            self.assertTrue(all(b <= a + 1e-10 for a, b in zip(energies, energies[1:])))


if __name__ == "__main__": unittest.main()
