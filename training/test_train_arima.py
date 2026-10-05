import unittest

import numpy as np
import pandas as pd

from train_arima import build_model, choose_candidate, predict


class ArimaContractTests(unittest.TestCase):
    def test_random_walk_equals_last_known_price_for_all_forecast_dates(self):
        train = pd.DataFrame({"ds": pd.date_range("2026-01-01", periods=60, freq="D"),
                              "y": 60000 + np.cumsum(np.sin(np.arange(60)) * 100)})
        result = build_model(train, (0, 1, 0)).fit()
        dates = pd.Series(pd.date_range("2026-03-02", periods=90, freq="D"))
        np.testing.assert_allclose(predict(result, dates), train.y.iloc[-1], rtol=0, atol=1e-6)

    def test_selection_excludes_failed_candidate_and_prefers_simpler_tie(self):
        candidates = [{"order": [1, 1, 1], "eligible": True, "mae_usd": 10},
                      {"order": [0, 1, 0], "eligible": True, "mae_usd": 10 + 5e-7},
                      {"order": [0, 1, 1], "eligible": False, "mae_usd": 0}]
        self.assertEqual(choose_candidate(candidates)["order"], [0, 1, 0])

    def test_no_converged_candidate_is_an_error(self):
        with self.assertRaises(ValueError):
            choose_candidate([{"eligible": False}])


if __name__ == "__main__":
    unittest.main()
