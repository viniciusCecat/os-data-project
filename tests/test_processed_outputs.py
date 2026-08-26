import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_READY = (
    (PROJECT_ROOT / "data" / "processed" / "project.duckdb").exists()
    and all(
        (PROJECT_ROOT / "data" / "processed" / "stackoverflow" / f"year={year}" / "survey_respondents.parquet").exists()
        and (
            PROJECT_ROOT
            / "data"
            / "processed"
            / "stackoverflow"
            / f"year={year}"
            / "survey_operating_systems.parquet"
        ).exists()
        for year in (2022, 2023, 2024, 2025)
    )
)


@unittest.skipUnless(DATA_READY, "requer surveys processados reais")
class ProcessedOutputsTest(unittest.TestCase):
    def test_processed_files_exist_for_all_years(self):
        for year in (2022, 2023, 2024, 2025):
            base = PROJECT_ROOT / "data" / "processed" / "stackoverflow" / f"year={year}"
            self.assertTrue((base / "survey_respondents.parquet").exists())
            self.assertTrue((base / "survey_operating_systems.parquet").exists())

    def test_project_duckdb_exists(self):
        self.assertTrue((PROJECT_ROOT / "data" / "processed" / "project.duckdb").exists())

    def test_no_duplicate_respondents_inside_year(self):
        import duckdb

        con = duckdb.connect(str(PROJECT_ROOT / "data" / "processed" / "project.duckdb"), read_only=True)
        duplicates = con.execute(
            """
            SELECT survey_year, respondent_id, count(*) AS n
            FROM survey_respondents
            GROUP BY survey_year, respondent_id
            HAVING n > 1
            """
        ).fetchall()
        con.close()
        self.assertEqual(duplicates, [])


if __name__ == "__main__":
    unittest.main()
