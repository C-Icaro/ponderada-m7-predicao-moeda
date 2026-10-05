"""Verifica cálculo de erro e barreiras temporais do experimento."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from train_compare import choose_window, metrics, training_before, write_report


class ComparisonTests(unittest.TestCase):
    def test_metrics_with_known_errors(self):
        result = metrics([100, 200], [110, 180])
        self.assertAlmostEqual(result["mae_usd"], 15.0)
        self.assertAlmostEqual(result["rmse_usd"], 15.811388300841896)
        self.assertAlmostEqual(result["smape_percent"], 10.025062656641604)

    def test_zero_denominator_and_invalid_predictions(self):
        self.assertEqual(metrics([0], [0])["smape_percent"], 0.0)
        with self.assertRaises(ValueError):
            metrics([1], [float("nan")])
        with self.assertRaises(ValueError):
            metrics([1, 2], [1])

    def test_training_excludes_first_forecast_day_and_later(self):
        frame = pd.DataFrame({"ds": pd.to_datetime(["2026-07-06", "2026-07-07", "2026-07-08"]),
                              "y": [100, 999, 999]})
        train = training_before(frame, pd.Timestamp("2026-07-07"))
        self.assertEqual(train.y.tolist(), [100])
        self.assertEqual(train.ds.max(), pd.Timestamp("2026-07-06"))

    def test_selection_uses_validation_and_breaks_ties_for_three_years(self):
        validation = {"models": {"3y": {"mae_usd": 10}, "12y": {"mae_usd": 10}}}
        self.assertEqual(choose_window(validation), "3y")
        validation["models"]["12y"]["mae_usd"] = 9
        self.assertEqual(choose_window(validation), "12y")

    def test_report_handles_zero_error_and_baseline_tie(self):
        zero = {"mae_usd": 0, "rmse_usd": 0, "smape_percent": 0}
        phase = {"models": {"3y": zero, "12y": zero}, "baseline": zero}
        result = {"selection": {"selected_window": "3y"}, "validation": phase, "test": phase}
        with TemporaryDirectory(prefix="ponderada-report-") as temporary:
            root = Path(temporary)
            (root / "reports").mkdir()
            write_report(root, result)
            text = (root / "reports" / "comparacao.md").read_text(encoding="utf-8")
            self.assertIn("diferença percentual não foi calculada", text)
            self.assertIn("empataram", text)


if __name__ == "__main__":
    unittest.main()
