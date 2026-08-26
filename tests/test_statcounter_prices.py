import csv
import datetime as dt
import unittest
from pathlib import Path

from src.statcounter import normalize_statcounter_os


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATCOUNTER_CSV = PROJECT_ROOT / "data" / "raw" / "statcounter" / "os_market_share.csv"
PRICES_CSV = PROJECT_ROOT / "data" / "raw" / "prices" / "os_prices.csv"


class StatCounterAndPricesTest(unittest.TestCase):
    def test_statcounter_normalization(self):
        self.assertEqual(normalize_statcounter_os("Windows").family, "Windows")
        self.assertEqual(normalize_statcounter_os("OS X").family, "macOS")
        self.assertEqual(normalize_statcounter_os("macOS").family, "macOS")
        self.assertEqual(normalize_statcounter_os("Chrome OS").family, "ChromeOS")
        self.assertEqual(normalize_statcounter_os("Solaris").family, "Other")

    @unittest.skipUnless(STATCOUNTER_CSV.exists(), "StatCounter CSV ausente")
    def test_statcounter_import_dates_and_ranges(self):
        with STATCOUNTER_CSV.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreater(len(rows), 0)
        for row in rows:
            dt.date.fromisoformat(row["date"])
            dt.date.fromisoformat(row["collected_at"])
            share = float(row["market_share"])
            self.assertGreaterEqual(share, 0)
            self.assertLessEqual(share, 100)
            self.assertIn(row["operating_system_family"], {"Windows", "Linux", "macOS", "ChromeOS", "BSD", "Other"})
            self.assertTrue(row["source"].startswith("https://gs.statcounter.com/"))

    @unittest.skipUnless(STATCOUNTER_CSV.exists(), "StatCounter CSV ausente")
    def test_statcounter_monthly_sum_tolerance(self):
        totals: dict[tuple[str, str], float] = {}
        with STATCOUNTER_CSV.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                key = (row["date"], row["region"])
                totals[key] = totals.get(key, 0.0) + float(row["market_share"])
        self.assertGreater(len(totals), 0)
        for total in totals.values():
            self.assertGreaterEqual(total, 95.0)
            self.assertLessEqual(total, 101.0)

    @unittest.skipUnless(PRICES_CSV.exists(), "CSV de precos ausente")
    def test_prices_are_valid(self):
        with PRICES_CSV.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreater(len(rows), 0)
        valid_currencies = {"USD", ""}
        for row in rows:
            dt.date.fromisoformat(row["collected_at"])
            self.assertIn(row["currency"], valid_currencies)
            self.assertTrue(row["source"].startswith("https://"))
            self.assertIn(row["open_source"], {"true", "false", "partial"})
            if row["software_price"]:
                self.assertGreaterEqual(float(row["software_price"]), 0)
            self.assertNotEqual(row["hardware_required"].strip(), "")
            self.assertIn("hardware_required", row)
            self.assertIn("software_price", row)


if __name__ == "__main__":
    unittest.main()
