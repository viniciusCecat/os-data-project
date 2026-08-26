from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedOS:
    operating_system_original: str
    operating_system_normalized: str
    operating_system_family: str


NULL_MARKERS = {"", "na", "n/a", "nan", "none", "null", "prefer not to say"}

EXACT_RULES = {
    "windows": ("Windows", "Windows"),
    "windows 10": ("Windows 10", "Windows"),
    "windows 11": ("Windows 11", "Windows"),
    "linux": ("Linux", "Linux"),
    "gnu/linux": ("Linux", "Linux"),
    "linux-based": ("Linux", "Linux"),
    "linux based": ("Linux", "Linux"),
    "ubuntu": ("Ubuntu", "Linux"),
    "debian": ("Debian", "Linux"),
    "fedora": ("Fedora", "Linux"),
    "arch": ("Arch", "Linux"),
    "arch linux": ("Arch", "Linux"),
    "red hat enterprise linux": ("Red Hat Enterprise Linux", "Linux"),
    "rhel": ("Red Hat Enterprise Linux", "Linux"),
    "centos": ("CentOS", "Linux"),
    "opensuse": ("openSUSE", "Linux"),
    "open suse": ("openSUSE", "Linux"),
    "macos": ("macOS", "macOS"),
    "mac os": ("macOS", "macOS"),
    "mac os x": ("macOS", "macOS"),
    "os x": ("macOS", "macOS"),
    "bsd": ("BSD", "BSD"),
    "freebsd": ("FreeBSD", "BSD"),
    "openbsd": ("OpenBSD", "BSD"),
    "netbsd": ("NetBSD", "BSD"),
    "chromeos": ("ChromeOS", "ChromeOS"),
    "chrome os": ("ChromeOS", "ChromeOS"),
    "chromeos flex": ("ChromeOS Flex", "ChromeOS"),
}

PATTERN_RULES = (
    (re.compile(r"^windows\s+10\b", re.IGNORECASE), ("Windows 10", "Windows")),
    (re.compile(r"^windows\s+11\b", re.IGNORECASE), ("Windows 11", "Windows")),
    (re.compile(r"^windows\b", re.IGNORECASE), ("Windows", "Windows")),
    (re.compile(r"^ubuntu\b", re.IGNORECASE), ("Ubuntu", "Linux")),
    (re.compile(r"^debian\b", re.IGNORECASE), ("Debian", "Linux")),
    (re.compile(r"^fedora\b", re.IGNORECASE), ("Fedora", "Linux")),
    (re.compile(r"^arch\s+linux\b", re.IGNORECASE), ("Arch", "Linux")),
    (re.compile(r"^mac\s?os\b|^macos\b|^os x\b", re.IGNORECASE), ("macOS", "macOS")),
    (re.compile(r"^freebsd\b", re.IGNORECASE), ("FreeBSD", "BSD")),
    (re.compile(r"^chrome\s?os\b", re.IGNORECASE), ("ChromeOS", "ChromeOS")),
)


def _is_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    text = str(value).strip()
    return text.lower() in NULL_MARKERS


def split_multiselect(value: Any) -> list[str]:
    """Divide respostas multi-select sem assumir que virgula separa sistemas."""
    if _is_null(value):
        return []
    if isinstance(value, (list, tuple, set)):
        raw_parts: list[str] = []
        for item in value:
            raw_parts.extend(split_multiselect(item))
        return raw_parts
    text = str(value).strip()
    delimiter = ";" if ";" in text else None
    parts = text.split(delimiter) if delimiter else [text]
    return [part.strip() for part in parts if part and part.strip()]


def normalize_os_token(token: Any) -> NormalizedOS | None:
    if _is_null(token):
        return None
    original = str(token).strip()
    canonical_key = re.sub(r"\s+", " ", original.casefold()).strip()
    if canonical_key in EXACT_RULES:
        normalized, family = EXACT_RULES[canonical_key]
        return NormalizedOS(original, normalized, family)
    for pattern, result in PATTERN_RULES:
        if pattern.search(original):
            normalized, family = result
            return NormalizedOS(original, normalized, family)
    if "other" in canonical_key or "please specify" in canonical_key:
        return NormalizedOS(original, "Other", "Other")
    return NormalizedOS(original, "Other", "Other")


def normalize_os(value: Any) -> list[NormalizedOS]:
    records: list[NormalizedOS] = []
    seen: set[tuple[str, str, str]] = set()
    for token in split_multiselect(value):
        normalized = normalize_os_token(token)
        if normalized is None:
            continue
        key = (
            normalized.operating_system_original,
            normalized.operating_system_normalized,
            normalized.operating_system_family,
        )
        if key not in seen:
            records.append(normalized)
            seen.add(key)
    return records

