import unittest
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from train_model import evaluate_dataset


class ModelEvaluationTest(unittest.TestCase):
    def test_uses_latest_year_as_temporal_holdout_and_imputes_missing_values(self):
        rows = []
        for year in (2022, 2023, 2024, 2025):
            for index in range(40):
                uses_linux = int(index % 2 == 0)
                rows.append(
                    {
                        "survey_year": year,
                        "country": "Brazil" if uses_linux else "United States",
                        "age": None if index % 5 == 0 else "25-34",
                        "employment": "Employed" if uses_linux else "Student",
                        "developer_type": "Developer" if uses_linux else "Student",
                        "professional_experience": "5 years" if uses_linux else "Less than 1 year",
                        "uses_linux": uses_linux,
                    }
                )
        rows[-1]["country"] = "Unseen test category"

        result = evaluate_dataset(pd.DataFrame(rows))

        self.assertEqual(result["test_year"], 2025)
        self.assertEqual(set(result["train"]["survey_year"]), {2022, 2023, 2024})
        self.assertEqual(set(result["test"]["survey_year"]), {2025})
        self.assertEqual(len(result["results"]), 3)
        self.assertTrue(all(0 <= row["f1_linux"] <= 1 for row in result["results"]))
        self.assertIn(result["chosen"]["model"], {"Regressao logistica", "Arvore de decisao"})

    def test_requires_multiple_survey_years(self):
        rows = [
            {
                "survey_year": 2025,
                "country": "Brazil",
                "age": "25-34",
                "employment": "Employed",
                "developer_type": "Developer",
                "professional_experience": "5 years",
                "uses_linux": 1,
            }
        ]
        with self.assertRaisesRegex(RuntimeError, "pelo menos dois anos"):
            evaluate_dataset(pd.DataFrame(rows))


if __name__ == "__main__":
    unittest.main()
