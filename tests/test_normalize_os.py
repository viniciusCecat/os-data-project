import math
import unittest

from src.normalize_os import normalize_os, split_multiselect


class NormalizeOSTest(unittest.TestCase):
    def test_null_values_are_accepted(self):
        self.assertEqual(normalize_os(None), [])
        self.assertEqual(normalize_os(""), [])
        self.assertEqual(normalize_os(math.nan), [])

    def test_multiselect_semicolon(self):
        self.assertEqual(split_multiselect("Windows;Ubuntu;macOS"), ["Windows", "Ubuntu", "macOS"])

    def test_windows_linux_macos_classification(self):
        records = normalize_os("Windows;Ubuntu;Mac OS")
        families = [record.operating_system_family for record in records]
        normalized = [record.operating_system_normalized for record in records]
        self.assertEqual(families, ["Windows", "Linux", "macOS"])
        self.assertEqual(normalized, ["Windows", "Ubuntu", "macOS"])

    def test_unknown_is_not_classified_as_linux(self):
        records = normalize_os("Solaris")
        self.assertEqual(records[0].operating_system_normalized, "Other")
        self.assertEqual(records[0].operating_system_family, "Other")
        self.assertEqual(records[0].operating_system_original, "Solaris")

    def test_duplicate_exact_tokens_are_removed(self):
        records = normalize_os("Windows;Windows")
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()

