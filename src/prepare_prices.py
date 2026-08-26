from __future__ import annotations

import csv
from datetime import date

from common import RAW_PRICES_DIR, exit_with_error


OUTPUT = RAW_PRICES_DIR / "os_prices.csv"
COLUMNS = [
    "collected_at",
    "system",
    "edition",
    "license_model",
    "open_source",
    "software_price",
    "currency",
    "hardware_required",
    "support_model",
    "source",
    "notes",
]


def price_rows(collected_at: str) -> list[dict[str, str]]:
    return [
        {
            "collected_at": collected_at,
            "system": "Windows",
            "edition": "Windows 11 Home",
            "license_model": "commercial proprietary retail license",
            "open_source": "false",
            "software_price": "139.00",
            "currency": "USD",
            "hardware_required": "compatible PC required",
            "support_model": "Microsoft consumer support; paid/enterprise support separate",
            "source": "https://www.microsoft.com/en-us/d/windows-11-home/dg7gmgf0krt0",
            "notes": "Microsoft Store US download price observed from official product page.",
        },
        {
            "collected_at": collected_at,
            "system": "Windows",
            "edition": "Windows 11 Pro",
            "license_model": "commercial proprietary retail license",
            "open_source": "false",
            "software_price": "199.99",
            "currency": "USD",
            "hardware_required": "compatible PC required",
            "support_model": "Microsoft consumer/business support; enterprise support separate",
            "source": "https://www.microsoft.com/en-us/d/windows-11-pro/dg7gmgf0d8h4",
            "notes": "Microsoft Store US download price observed from official product page.",
        },
        {
            "collected_at": collected_at,
            "system": "macOS",
            "edition": "Current compatible macOS upgrade",
            "license_model": "proprietary software bundled for compatible Apple Mac hardware",
            "open_source": "partial",
            "software_price": "0",
            "currency": "USD",
            "hardware_required": "compatible Mac required",
            "support_model": "Apple software updates; hardware support depends on device coverage",
            "source": "https://support.apple.com/en-us/102662",
            "notes": "Software Update provides compatible macOS updates/upgrades; hardware cost is not treated as software price.",
        },
        {
            "collected_at": collected_at,
            "system": "Ubuntu",
            "edition": "Ubuntu Desktop",
            "license_model": "free open source operating system",
            "open_source": "true",
            "software_price": "0",
            "currency": "USD",
            "hardware_required": "compatible PC required",
            "support_model": "community support; paid Canonical services optional",
            "source": "https://ubuntu.com/desktop",
            "notes": "Ubuntu Desktop page states Ubuntu has always been free to download, use and share.",
        },
        {
            "collected_at": collected_at,
            "system": "Ubuntu Pro",
            "edition": "Personal",
            "license_model": "no-cost subscription for personal use with machine limit",
            "open_source": "true",
            "software_price": "0",
            "currency": "USD",
            "hardware_required": "compatible Ubuntu machine required",
            "support_model": "expanded security maintenance; no-cost personal tier up to the stated machine limit",
            "source": "https://ubuntu.com/pro",
            "notes": "Official Ubuntu Pro page states it is free for personal use on up to 5 physical machines.",
        },
        {
            "collected_at": collected_at,
            "system": "Ubuntu Pro",
            "edition": "Workstation",
            "license_model": "commercial subscription",
            "open_source": "true",
            "software_price": "25.00",
            "currency": "USD",
            "hardware_required": "compatible Ubuntu workstation required",
            "support_model": "subscription; optional support tiers may add cost",
            "source": "https://ubuntu.com/pricing/pro",
            "notes": "Official pricing lists Workstation at USD 25 per machine per year.",
        },
        {
            "collected_at": collected_at,
            "system": "Red Hat Enterprise Linux",
            "edition": "Workstation",
            "license_model": "commercial subscription",
            "open_source": "true",
            "software_price": "196.90",
            "currency": "USD",
            "hardware_required": "compatible workstation required",
            "support_model": "Red Hat subscription; support level depends on selected SKU",
            "source": "https://www.redhat.com/en/store/linux-platforms",
            "notes": "Official Red Hat store lists RHEL Workstation starting price.",
        },
        {
            "collected_at": collected_at,
            "system": "ChromeOS Flex",
            "edition": "ChromeOS Flex",
            "license_model": "proprietary Google operating system offered for compatible existing devices",
            "open_source": "partial",
            "software_price": "0",
            "currency": "USD",
            "hardware_required": "compatible PC or Mac required",
            "support_model": "Google documentation; Chrome Enterprise management may be separate",
            "source": "https://chromeos.google/intl/en_uk/products/chromeos-flex/",
            "notes": "Official ChromeOS Flex page says get started free of charge.",
        },
        {
            "collected_at": collected_at,
            "system": "FreeBSD",
            "edition": "FreeBSD",
            "license_model": "open source BSD license",
            "open_source": "true",
            "software_price": "0",
            "currency": "USD",
            "hardware_required": "supported hardware required",
            "support_model": "community project; commercial third-party support may exist separately",
            "source": "https://www.freebsd.org/",
            "notes": "Official FreeBSD page describes it as a powerful open source operating system.",
        },
    ]


def main() -> int:
    RAW_PRICES_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(price_rows(date.today().isoformat()))
    print(f"Precos/licenciamento salvos em: {OUTPUT}")
    print(f"Linhas: {len(price_rows(date.today().isoformat()))}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(exit_with_error(exc))

