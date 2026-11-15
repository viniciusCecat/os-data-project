import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common import PipelineError
from investigate_gaming_linux import estimate_all_dates


class GamingLinuxTrendTest(unittest.TestCase):
    def test_reports_expected_months_without_matching_versions(self):
        skipped = []
        rows = estimate_all_dates(
            {"2022-01-01": {"Windows 11": 80.0}},
            {("2022-01-01", "pc"): {"Windows 10": 100.0}},
            skipped,
        )

        self.assertEqual(rows, [])
        self.assertTrue(any("nenhuma versao em comum para Windows" in item for item in skipped))
        self.assertEqual(len(skipped), 3)

    def test_invalid_platform_share_is_not_silently_discarded(self):
        with self.assertRaisesRegex(PipelineError, "Soma invalida"):
            estimate_all_dates(
                {"2022-01-01": {"Windows 11": 80.0}},
                {("2022-01-01", "pc"): {"Windows 11": 0.0}},
                [],
            )


if __name__ == "__main__":
    unittest.main()
