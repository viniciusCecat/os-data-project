from __future__ import annotations

from dataclasses import dataclass


STATCOUNTER_FAMILIES = {
    "windows": "Windows",
    "linux": "Linux",
    "macos": "macOS",
    "mac os": "macOS",
    "os x": "macOS",
    "chrome os": "ChromeOS",
    "chromeos": "ChromeOS",
    "freebsd": "BSD",
    "openbsd": "BSD",
    "netbsd": "BSD",
}


@dataclass(frozen=True)
class StatCounterOS:
    original: str
    family: str


def normalize_statcounter_os(value: str) -> StatCounterOS:
    original = str(value).strip()
    family = STATCOUNTER_FAMILIES.get(original.casefold(), "Other")
    return StatCounterOS(original=original, family=family)

