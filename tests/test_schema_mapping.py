import unittest

from src.schema_mapping import infer_mapping


class SchemaMappingTest(unittest.TestCase):
    def test_minimal_schema_is_identified(self):
        columns = [
            "ResponseId",
            "Country",
            "Employment",
            "DevType",
            "YearsCodePro",
            "Age",
            "OpSysProfessional use",
        ]
        mapping = infer_mapping(columns)
        self.assertEqual(mapping.respondent_id, "ResponseId")
        self.assertEqual(mapping.operating_system, "OpSysProfessional use")
        self.assertEqual(mapping.country, "Country")

    def test_operating_system_fallback_uses_real_column(self):
        columns = ["ResponseId", "Operating System Used Professionally"]
        mapping = infer_mapping(columns)
        self.assertEqual(mapping.operating_system, "Operating System Used Professionally")


if __name__ == "__main__":
    unittest.main()

